#!/usr/bin/env python
from random import choice, randrange
from string import punctuation

import discord
import os
import requests
from dotenv import load_dotenv

from matrix_markov import MatrixMarkov

STATIC_QUERY = "http://20.84.107.89:8983/solr/nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=nutch"
EMPTY_DOC = {'response': {
    'docs': [{'content': "no content", "url": "NO URL"}]}}


class DiscordClient:
    def __init__(self):
        load_dotenv()
        self.bot = discord.Bot()
        self.matMark = MatrixMarkov()

    def load_docs(self):
        response = requests.get(STATIC_QUERY)
        # super basic safety check
        if response.status_code == 200:
            docs_json = response.json()
        else:
            docs_json = EMPTY_DOC

        for doc in [x for x in docs_json['response']['docs']]:
            cont = doc['content']
            src = doc['url']
            self.matMark.add_document(cont, src, defer_recalc=True)
        self.matMark.recalc_probabilities()

    def get_resp(self, incomming_message, show_sources=False):
        # this really isn't searching -- we're just generating candidate text
        input_toks = [x.strip(punctuation) for x in incomming_message.split()]
        start_tok = choice(input_toks)
        # fixme: should use an input tok
        paragraph_data = self.get_paragraph()

        response_lines = list()
        response_lines.append("GENERATED FROM CORPUS:")
        if len(paragraph_data['sentences']) == 0:
            response_lines.append(
                f"**token {start_tok} did not match any in the corpus :(**"
            )
            return "\n".join(response_lines)
        else:
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
        sentences = list()
        unsorted_citations = list()

        start_tok = choice(list(self.matMark.token_index_map.keys()))

        resp_dict = self.matMark.get_markov_chain(100, start_tok)
        resp_dict['markov_chain'][0] = "    " + resp_dict['markov_chain'][0]
        sentences.append(" ".join(resp_dict['markov_chain']))

        unsorted_citations = unsorted_citations + \
            list(dict(resp_dict['sources']).items())

        for _ in range(0, randrange(5, 15)):
            start_tok = choice(list(self.matMark.token_index_map.keys()))
            resp_dict = self.matMark.get_markov_chain(100, start_tok)
            sentences.append(" ".join(resp_dict['markov_chain']))
            unsorted_citations = unsorted_citations + \
                list(dict(resp_dict['sources']).items())

        resp = {'sentences': list(), 'citations': list()}
        resp['sentences'] = sentences
        resp['citations'] = unsorted_citations
        return resp

    def dedupe_and_sort_citations(self, citation_list: list) -> list:
        uniq_references = dict()

        for ref in citation_list:
            if uniq_references.get(ref[0], None):
                uniq_references[ref[0]] = uniq_references[ref[0]] + ref[1]
            else:
                uniq_references[ref[0]] = ref[1]

        sorted_citations = list()
        for k, v in uniq_references.items():
            sort_tuple = (v, k)
            sorted_citations.append(sort_tuple)

        sorted_citations = sorted(sorted_citations, reverse=True)
        return [{v: k} for k, v in sorted_citations]


def main():
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
        await ctx.respond(f"reloaded docs with static query")

    bot.add_application_command(loom)
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
