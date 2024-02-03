#!/usr/bin/env python
from random import randrange

import discord
import os
from dotenv import load_dotenv

from markov import Markov


load_dotenv()
bot = discord.Bot()
try:
    brain = os.getenv('BRAIN_PATH')
    backup = os.getenv('BACKUP_PATH')
except:
    print("brain and backup paths must be set")
    exit(1)

brain = Markov(input_file=brain, output_file=backup, ignore_words=[])

fake_sources = [
        "WARNING: these ae fake sources",
        "https://www.poetryfoundation.org/poems/44475/la-belle-dame-sans-merci-a-ballad",
        "https://www.poetryfoundation.org/poems/48860/the-raven",
        "https://www.madisonpubliclibrary.org/engagement/poetry/poem-a-day/where-sidewalk-ends",
        ]
fake_source_string = "\n".join(fake_sources)

# generate 1-4 'sentences"
def get_resp(incomming_message):
    statements = []

    statements.append(brain.create_response(incomming_message, learn=True))
    for _ in range(1, randrange(1,5)):
        statements.append(brain.create_response(incomming_message, learn=False))
    return( "**<--Markov chain from source-->**\n\n" + ". ".join(statements) + ".")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name = "search", description = "Query the bot's Bayesian network")
async def search(ctx, search_string: str, show_sources: bool):
    await ctx.respond(get_resp(search_string))
    if show_sources:
        await ctx.respond(fake_source_string)

bot.run(os.getenv('TOKEN'))
