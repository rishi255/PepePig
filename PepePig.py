# bot.py
import os
import asyncio
import discord.file
import typing
import discord
import re
from discord.ext import commands
from discord.utils import get
from googletrans import Translator, LANGCODES, LANGUAGES

TOKEN = os.getenv('DISCORD_TOKEN')

pepe = commands.Bot(command_prefix='pepe ', help_command=None, description="I'm a cute bot made by @rishee#8641")

@pepe.event
async def on_ready():
    print(f'{pepe.user} has connected to Discord!')
    game = discord.Game(name = "with ur mum")
    await pepe.change_presence(activity=game)

@pepe.event
async def on_message(message):
    if message.author == pepe.user: # ignore own messages (to prevent infinite loop)
        return
    
    msg = message.content
    if msg.lower().startswith('ayy') and msg.lower().endswith('y'):
        await message.channel.send(f'lmao {message.author.mention}')
    elif "who" in msg.lower() and "daddy" in msg.lower():
        Rishi = pepe.get_user(425968693424685056)
        await message.channel.send(f'{Rishi.mention} is my daddy.')
    elif msg.lower().startswith('bruh') and msg.lower().endswith('h'):
        img = discord.File(open("media\satsriakal bruh.jpg", "rb"), filename="satsriakal.jpg")
        await message.channel.send(file=img)
        await message.channel.send(f'**Bruh moment successfully reported by {message.author.mention}**')
    else:
        obj = re.search(r"(valo(rant)?[?]?[\s]?[\$]?)", msg, re.IGNORECASE)
        if obj:
            await message.channel.send(f"{message.author.mention} haan ruk bro mai aara")
    
    await pepe.process_commands(message)

class MyHelpCommand(commands.DefaultHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} - {1.signature}'.format(self, command)
    @commands.command(name = 'help', hidden=True)
    async def help(self, ctx):
        await ctx.send("HELP SCREEN")

class HelpCog(commands.Cog, command_attrs=dict(name="Help", usage="pepe help", hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

class PepeTasks(commands.Cog):
    """
    Contains first year tasks for bot-ragging purposes.
    """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
    pass_context=True, 
    name = 'giveintro',
    help = "Gives intro in various languages like a good first year boi.",
    usage = "pepe giveintro <language-name>"
    )
    async def giveintro(self, ctx):
        msg = ctx.message
        words = msg.content.split(' ')
        to_language = words[-1] # pepe giveintro <langauge>

        intro_text = "I'm Pepe Pig (**cRoaK**).\nThis is my little brother George (**mEeP mEeP**),\nthis is mummy pig (**bruh sound effect #2**),\nand this is DADDY FROG (**huge snort**)"
    
        # LANGCODES has keys as languages, values as codes
        try:
            # LANGCODES has keys as languages, values as codes
            # LANGUAGES has keys as codes, values as languages 
        
            if to_language in LANGCODES: # if language name was passed
                code = LANGCODES[to_language]
            elif to_language in LANGUAGES: # if code was passed
                code = to_language

            trans = Translator()
            translated_intro = trans.translate(intro_text, dest=code)
            await ctx.send(translated_intro.text)

        except:
            await ctx.send("Please enter a valid language!" +
            "\nSyntax: pepe giveintro <language-name>" +
            "\nFor a list of supported languages, use \"pepe languages\"")

    @commands.command(
    pass_context=True, 
    name = 'languages',
    help = "Lists all supported languages for intro"
    )
    async def languages(self, ctx):
        text = [(lang, code) for lang, code in LANGCODES.items()]
        await ctx.send('\n'.join([f"{code}: {lang}" for code, lang in text]))
    

class UtilityCommands(commands.Cog):
    """ 
    Contains some useful commands (lmao jk)
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
    pass_context=True, 
    name = 'clear',
    help = "Clears the n most recent messages from specific/all users"
    )
    async def clear(self, ctx, user: typing.Optional[discord.Member], number: typing.Optional[int] = 1):
        if user is None:
            deleted = await ctx.channel.purge(limit=number+1)
            await ctx.send('{} deleted the last {} message(s) lol. Ab tu suspense me hi mar'.format(ctx.message.author.name, number))
        else:
            count = 0
            to_delete = []

            if user.id == ctx.message.author.id: number += 1

            async for message in ctx.channel.history(): #default limit 100
                if count == number:
                    break
                if message.author.id == user.id:
                    to_delete.append(message)
                    count += 1

            await ctx.channel.delete_messages(to_delete)
            await ctx.send('{} deleted the last {} message(s) from user {} lol. Ab tu suspense me hi mar'.format(ctx.message.author.name, number, user.display_name))#+'\n'.join([i.content for i in to_delete]))

    @commands.command(
    pass_context=True,
    name = 'translate',
    help = "Translates from detected language to whatever language you want!",
    usage = "pepe translate <text IN QUOTES> <destination-language>"
    )
    async def translate(self, ctx):
        msg = ctx.message
        words = msg.content.split(' ')
        to_language = words[-1].lower()
        text = str()
        
        arr = msg.content.split("\"")
        if len(arr) == 3:
            text = arr[1]
        else:
            text = ' '.join(words[2:-1])
        
        try:
            # LANGCODES has keys as languages, values as codes
            # LANGUAGES has keys as codes, values as languages 
        
            if to_language in LANGCODES: # if language name was passed
                code = LANGCODES[to_language]
            elif to_language in LANGUAGES: # if code was passed
                code = to_language

            trans = Translator()
            translated_text = trans.translate(text, dest=code)
            await ctx.send(translated_text.text)#, tts=True)
        except:
            await ctx.send("Please enter a valid language!" +
            "\nSyntax: pepe translate <text> <language-name>" +
            "\nFor a list of supported languages, use \"pepe languages\"")


def setup(pepe):
    pepe.remove_command('help')
    pepe.add_cog(PepeTasks(pepe))
    pepe.add_cog(UtilityCommands(pepe))
    pepe.add_cog(HelpCog(pepe))
    
setup(pepe)
pepe.run(TOKEN)