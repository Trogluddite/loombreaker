#!/usr/bin/env python
"""
  provides the loombot interface to discord
  uses a DiscordClient class to interface with MatrixMarkov
  uses Requests to load documents from SOLR
"""
from random import choice, randrange
from string import punctuation
import subprocess
import os

import discord
import requests
from dotenv import load_dotenv

from matrix_markov import MatrixMarkov

SOLR_URL = "http://20.84.107.89:8983/solr/"
# SOLR_QUERY = "nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=hydrogen&rows=2"
SOLR_QUERY = "nutch/select?fl=content%2Ctitle%2Curl&fq=url%3A%22https%3A%2F%2Fen.m.wikipedia.org*%22&indent=true&q.op=OR&q=Argon"


STATIC_QUERY_STR = f"{SOLR_URL}{SOLR_QUERY}"

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

    def get_resp(self, incomming_message, show_sources=False):
        """
            get a response from the MatrixMarkov instance, and format it for delivery
            back to the discord client.

            uses instance methods "get_paragraph" & "dedupe_and_sort_citations"
        """
        input_toks = [x.strip(punctuation) for x in incomming_message.split()]
        start_tok = choice(input_toks)
        # fixme: should use an input tok
        paragraph_data = self.get_paragraph()

        response_lines = []
        response_lines.append("GENERATED FROM CORPUS:")
        if len(paragraph_data['sentences']) == 0:
            response_lines.append(
                f"**token {start_tok} did not match any in the corpus :(**"
            )
            return "\n".join(response_lines)
        # response is python list with words in it
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

        for _ in range(0, randrange(5, 15)):
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


class CrawlerControl:
    """
        provides control interface to webcrawler
    """

    def __init__(self):
        pass

    def start_crawl(self):
        _ = subprocess.Popen(["../automation_tests/automate.py"])

    def check_crawl(self):
        crawler_state = ""
        with open("../automation_tests/crawler_state.txt", "r") as statefile:
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

    @loom.command()
    async def search(ctx, search_string: str, show_sources: bool):
        await ctx.respond(dc.get_resp(search_string, show_sources))

    @loom.command()
    async def reload_docs(ctx):
        dc.load_docs()
        await ctx.respond("reloaded docs with static query")

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
