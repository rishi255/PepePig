# bot.py
import os
import asyncio
import discord.file
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pepe = commands.Bot(command_prefix='pepe ', description="A python bot made by @rishee#8641")

@pepe.event
async def on_ready():
    print(f'{pepe.user} has connected to Discord!')
    game = discord.Game(name = "with ur mum")
    await pepe.change_presence(activity=game)

@pepe.command(help="Just responds with pong")
async def ping(ctx):
    msg = ctx.message.content
    words = msg.split(' ')
    await ctx.send('pong')

class PepeTasks:
    """
    Contains first year tasks for bot-ragging purposes.
    """
    @pepe.command(pass_context=True, help="Gives intro in various languages like a good first year boi")
    async def giveintro(self, ctx):
        msg = ctx.message
        words = msg.content.split(' ')
        if words[2] == "english":
            fp = open("media\pepevideo_trim.mp4", "rb")
            video = discord.File(fp, filename="intro.mp4")
            await ctx.send("I'm Pepe Pig (**cRoaK**).\nThis is my little brother George (**mEeP mEeP**),\nthis is mummy pig (**bruh sound effect #2**),\nand this is DADDY FROG (**huge snort**)", tts=True)
            await ctx.send(file=video)
        elif words[2] == "spanish":
            fp = open("media\spanishsound.mp3", "rb")
            sound = discord.File(fp, filename="spanish sound.mp3")
            await ctx.send("Soy Pepe Pig (**cRoaK**). \n Este es mi hermano menor George (**mEeP mEeP**),\neste es el cerdo de momia (**efecto de sonido bruh #2**), \ny esto es RANA PAPÁ (**gran resoplido**)")
            await ctx.send(file=sound)
        elif words[2] == "hindi":
            fp = open("media\hindisound.mp3", "rb")
            sound = discord.File(fp, filename="hindi sound.mp3")
            await ctx.send("मैं पेपे सुअर हूं (**cRoaK**) ।\nयह मेरा छोटा भाई जॉर्ज है (**mEeP mEeP**),\nयह ममी सुअर है (**bruh sound effect #2**),\nयह है डैडी फ्रॉग (**विशाल स्नॉर्ट**)")
            await ctx.send(file=sound)
    
pepe.add_cog(PepeTasks())
pepe.run(TOKEN)
