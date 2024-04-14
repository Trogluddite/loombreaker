#!/usr/bin/env python
"""
  provides the loombot interface to discord
  uses a DiscordClient class to interface with MatrixMarkov
  uses Requests to load documents from SOLR
"""
from random import choice, randrange
from string import punctuation
from math import sqrt
import subprocess
import os

import discord
import requests
from dotenv import load_dotenv
from numpy import array as np_array
from numpy import dot as np_dot

from matrix_markov import MatrixMarkov

SOLR_URL = "http://20.84.107.89:8983/solr/"
# SOLR_QUERY = "nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=hydrogen&rows=2"
SOLR_QUERY = "nutch/select?fl=content%2Ctitle%2Curl&fq=url%3A%22https%3A%2F%2Fen.m.wikipedia.org*%22&indent=true&q.op=OR&q="
query_content = "Argon"

STATIC_QUERY_STR = f"{SOLR_URL}{SOLR_QUERY}{query_content}"

EMPTY_DOC = {'response': {
    'docs': [{'content': "no content", "url": "NO URL"}]}}
SOLR_QUERY_TIMEOUT = 180


class DiscordClient:
    """
        stores discord bot instance
        stores, and interfaces with, MatrixMarkov instance
        providees interface to MatrixMarkov, and to SOLR
    """

    def __init__(self):
        load_dotenv()
        self.bot = discord.Bot()
        self.mat_mark = MatrixMarkov()

    def load_docs(self):
        """
        retrieves documents from the source (in this case, SOLR)
        and then inserts them into the MatrixMarkov instance
        """
        response = requests.get(STATIC_QUERY_STR, timeout=SOLR_QUERY_TIMEOUT)
        # super basic safety check
        if response.status_code == 200:
            docs_json = response.json()
        else:
            docs_json = EMPTY_DOC

        for doc in list(docs_json['response']['docs']):
            cont = doc['content']
            src = doc['url']
            self.mat_mark.add_document(cont, src, defer_recalc=True)
        self.mat_mark.recalc_probabilities()
      
    def update_query(new_query):
      STATIC_QUERY_STR = f"{SOLR_URL}{SOLR_QUERY}{new_query}"

    def get_resp(self, match_target, show_sources=False,
                 max_rounds=250, target_score=0.85):
        """
            get a response from the MatrixMarkov instance, and format it for delivery
            back to the discord client.

            uses instance methods "get_paragraph" & "dedupe_and_sort_citations"
        """
        best_match_score = 0.0
        best_match_paragraph = {}
        iter = 0
        while best_match_score < target_score and iter < max_rounds:
            p = self.get_paragraph()
            similarity = self.get_cos_similarity(match_target, " ".join(p['sentences']))
            if similarity > best_match_score:
                best_match_score = similarity
                best_match_paragraph = p
            iter += 1
            if iter % 25 == 0:
                print(f"iter {iter} passed")

        paragraph_data = best_match_paragraph

        response_lines = []
        response_lines.append(f"Best Match Score: {best_match_score}")
        response_lines.append(f"{ ' '.join(paragraph_data['sentences'])}")

        if show_sources:
            top_citations = self.dedupe_and_sort_citations(
                paragraph_data['citations'])[0:3]
            for i in range(0, 3):
                if i >= len(top_citations):
                    response_lines.append(
                        f"    Only {i} sources for this chain!")
                    break
                k, v = list(top_citations[i].items())[0]
                response_lines.append(f"    {k}: counted {v} times")

        return "\n".join(response_lines)

    def get_paragraph(self):
        """
            get a pseudo-paragraph and it's citations.
            passes on unsorted citations list with possible duplications
            (that workflow seems wonky)
        """
        sentences = []
        unsorted_citations = []

        start_tok = choice(list(self.mat_mark.token_index_map.keys()))

        resp_dict = self.mat_mark.get_markov_chain(100, start_tok)
        resp_dict['markov_chain'][0] = "    " + resp_dict['markov_chain'][0]
        sentences.append(" ".join(resp_dict['markov_chain']))

        unsorted_citations = unsorted_citations + \
            list(dict(resp_dict['sources']).items())

        for _ in range(0, randrange(3, 7)):
            start_tok = choice(list(self.mat_mark.token_index_map.keys()))
            resp_dict = self.mat_mark.get_markov_chain(100, start_tok)
            sentences.append(" ".join(resp_dict['markov_chain']))
            unsorted_citations = unsorted_citations + \
                list(dict(resp_dict['sources']).items())

        resp = {'sentences': [], 'citations': []}
        resp['sentences'] = sentences
        resp['citations'] = unsorted_citations
        return resp

    def dedupe_and_sort_citations(self, citation_list: list) -> list:
        """
            citations are lists of dicts, with each being {source_url : count}
            this de-duplicates keys and folds counts into unique keys
        """
        uniq_references = {}

        for ref in citation_list:
            if uniq_references.get(ref[0], None):
                uniq_references[ref[0]] = uniq_references[ref[0]] + ref[1]
            else:
                uniq_references[ref[0]] = ref[1]

        sorted_citations = []
        for k, v in uniq_references.items():
            sort_tuple = (v, k)
            sorted_citations.append(sort_tuple)

        sorted_citations = sorted(sorted_citations, reverse=True)
        return [{v: k} for k, v in sorted_citations]

    def get_cos_similarity(self, target : str, compareTo : str):
        search_tokens = list(set(target.split() + compareTo.split()))
        targetCounts = {}
        for k in search_tokens:
            targetCounts[k] = target.count(k)
        compareToCounts = {}
        for k in search_tokens:
            compareToCounts[k] = compareTo.count(k)

        target_vect = np_array([targetCounts[x] for x in targetCounts.keys()])
        compare_to_vect = np_array([compareToCounts[x] for x in compareToCounts.keys()])
        num = np_dot(target_vect, compare_to_vect)
        denom = sqrt(target_vect.dot(target_vect)) * sqrt(compare_to_vect.dot(compare_to_vect))

        return num/denom


class CrawlerControl:
    """
        provides control interface to webcrawler
    """

    def __init__(self):
        pass

    def start_crawl(self):
        """
        start up the nutch crawler script
        """
        _ = subprocess.Popen(["../automation_tests/automate.py"]) #pylint: disable=consider-using-with

    def check_crawl(self):
        """
        check the current status of the crawl operation
        """
        with open("status.txt", "r", encoding="utf-8") as statefile:
            crawler_state = statefile.read()
        return crawler_state


def main():  # pylint: disable=missing-function-docstring
    cc = CrawlerControl()
    dc = DiscordClient()
    dc.load_docs()
    bot = dc.bot

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")

    loom = discord.SlashCommandGroup("loom", "search related commands")

    # Pycord seems to be abusing the type annotatiions here; pyright doesn't care for it
    @loom.command()
    async def search(ctx,
                     match_target: discord.Option(str),
                     show_sources: discord.Option(bool),
                     max_rounds: discord.Option(int)=50,
                     target_score: discord.Option(float)=0.85):
        await ctx.defer()
        await ctx.followup.send(
                dc.get_resp(match_target, show_sources, max_rounds, target_score))

    @loom.command()
    async def reload_docs(ctx):
        await ctx.defer()
        dc.load_docs()
        await ctx.followup.send("reloaded docs with status query!")

    @loom.command()
    async def change_query(ctx, new_query: discord.Option(str)):
        await ctx.defer()
        dc.update_query(new_query)
        await ctx.defer()
        dc.load_docs()
        await ctx.followup.send("Query Updated, documents have been automatically reloaded!")

    @loom.command()
    async def start_crawl(ctx):
        cc.start_crawl()
        await ctx.respond("started crawler; use /check_crawl to check status")

    @loom.command()
    async def check_crawl(ctx):
        await ctx.respond(cc.check_crawl())

    bot.add_application_command(loom)
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()
