#!/usr/bin/env python
from random import choice
from string import punctuation

import discord
import os
import requests
from dotenv import load_dotenv

from matrix_markov import MatrixMarkov

STATIC_QUERY = "http://20.84.107.89:8983/solr/nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=nutch"
EMPTY_DOC = {'response' : { 'docs' : [{'content':"no content", "url" : "NO URL"}]}}

class DiscordClient:
    def __init__(self):
        load_dotenv()
        self.bot = discord.Bot()
        self.matMark = MatrixMarkov()

    def load_docs(self):
        response = requests.get(STATIC_QUERY)
        ## super basic safety check
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
        resp_dict = self.matMark.get_markov_chain(max_len=200, start_token=start_tok)

        response_lines = list()
        response_lines.append("GENERATED FROM CORPUS:")
        if len(resp_dict['markov_chain']) == 0:
            response_lines.append(
                f"**token {start_tok} did not match any in the corpus :(**"
            )
            return "\n".join(response_lines)
        else:
            # response is python list with words in it
            response_lines.append(f"{ ' '.join(resp_dict['markov_chain'])}")

        if show_sources:
            sorted_citations = list()
            for k,v in resp_dict['sources'].items():
                sort_tuple = (v, k) # invert citation / count so we can sort by count
                sorted_citations.append(sort_tuple)
            sorted_citations = sorted(sorted_citations, reverse=True)
            for i in range(0,3):
                if i >= len(sorted_citations):
                    response_lines.append(f"    Only {i} sources for this chain!")
                    break
                k,v = sorted_citations[i]
                response_lines.append(f"    {v}: counted {k} times") #unpack sort tuple to reverse key/value
        return "\n".join(response_lines)

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
