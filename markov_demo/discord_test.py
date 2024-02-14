#!/usr/bin/env python
import json
from random import choice
from string import punctuation

import discord
import os
from dotenv import load_dotenv

from matrix_markov import MatrixMarkov


load_dotenv()
bot = discord.Bot()

# loading static docs for now, source_docs.json has a list of 10 wikipedia pages
docs_map_path = './test_docs/source_docs.json'
with open(docs_map_path, 'r') as json_doc:
    docs_json = json.load(json_doc)

matMark = MatrixMarkov()
for doc in [x for x in docs_json['documents']]:
    tf = doc['filename']
    src = doc['url']
    with open('./test_docs/'+ tf, 'r') as infile:
        contents = infile.read()
        matMark.add_document(contents, src, defer_recalc=True)
    matMark.recalc_probabilities()


def get_resp(incomming_message, show_sources=False):
    # this really isn't searching -- we're just generating candidate text
    input_toks = [x.strip(punctuation) for x in incomming_message.split()]
    start_tok = choice(input_toks)
    resp_dict = matMark.get_markov_chain(max_len=200, start_token=start_tok)


    response_lines = list()
    response_lines.append("GENERATED FROM CORPUS:")
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


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name = "search", description = "Query the bot's Bayesian network")
async def search(ctx, search_string: str, show_sources: bool):
    await ctx.respond(get_resp(search_string, show_sources))

bot.run(os.getenv('TOKEN'))
