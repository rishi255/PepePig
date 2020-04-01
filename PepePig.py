# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

PEPE_PIG = discord.Client()

@PEPE_PIG.event
async def on_ready():
    print(f'{PEPE_PIG.user} has connected to Discord!')

@PEPE_PIG.event
async def on_message(msg):
    print(msg.content)

# @PEPE_PIG.command()
# async def length(ctx):
#     await ctx.send('Your message is {} characters long.'.format(len(ctx.message.content)))

PEPE_PIG.run(TOKEN)
