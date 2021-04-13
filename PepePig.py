# bot.py
import asyncio
import asyncpg
import discord
from discord.ext import commands
from googletrans import Translator, LANGCODES, LANGUAGES
import json
import os
import random
import re
import traceback
import typing
from urllib import request

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

pepe = commands.Bot(command_prefix='pepe ', help_command=None, description="I'm a cute bot made by @rishee#8641", intents=intents)

@pepe.event
async def on_ready():
    print(f'{pepe.user} has connected to Discord!')
    game = discord.Game(name = "with ur mum")
    await pepe.change_presence(activity=game)

async def init_db() -> asyncpg.connection.Connection:
    conn = await asyncpg.connect(dsn=os.getenv('DATABASE_URL'))
    await conn.execute(
    '''CREATE TABLE IF NOT EXISTS pepepig_users (
            s_no SERIAL PRIMARY KEY, 
            member_id bigint, 
            score bigint,
            server_id bigint
        )
    ''')
    # print("Create table if not exists done.")
    return conn

@pepe.event
async def on_message(message):
    
    # don't process own messages (to prevent infinite loop, 
    # and to make sure pepe isn't in the scores database)
    if message.author == pepe.user:
        return

    author_id = message.author.id
    guild_id = message.guild.id

    try:
        conn = await init_db()

        exists = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pepepig_users WHERE member_id=$1 AND server_id=$2)", author_id, guild_id)
        # print(f"Does user {message.author} exist in db? [{exists}]")

        increment_val = random.randint(20, 50)

        if exists:
            new_score = await conn.fetchval("UPDATE pepepig_users SET score=score+$1 WHERE member_id=$2 AND server_id=$3 RETURNING score", increment_val, author_id, guild_id)
            # print(f"User already has a score in this server! New score for {message.author.display_name} = {new_score}")
        else:
            new_score = await conn.fetchval("INSERT INTO pepepig_users (member_id, score, server_id) VALUES ($1, $2, $3) RETURNING score", author_id, increment_val, guild_id)
            # print(f"New user entry for this server! New score for {message.author.display_name} = {new_score}")
        
        await conn.close()
    except Exception as e:
        print(e)
        print("\nCOULDN'T CONNECT TO DATABASE!")

    msg = message.content
    # ayy -> lmao
    if msg.lower().startswith('ayy') and msg.lower().endswith('y'):
        await message.channel.send(f'lmao {message.author.mention}')
    # who daddy -> rishee
    elif "who" in msg.lower() and "daddy" in msg.lower():
        Rishi = pepe.get_user(425968693424685056)
        await message.channel.send(f'{Rishi.mention} is my daddy.')
    # For reporting bruh moment
    elif msg.lower().startswith('bruh') and msg.lower().endswith('h'):
        img = discord.File(open("media/satsriakal bruh.jpg", "rb"), filename="satsriakal.jpg")
        await message.channel.send(file=img)
        await message.channel.send(f'**Bruh moment successfully reported by {message.author.mention}**')
    # For valo
    elif re.search(r"(valo(rant)?[?]?[\s]?[\$]?)", msg, re.IGNORECASE) or "<@&763655495285473300>" in msg.lower():
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
            code = None
            if to_language in LANGCODES: # if language name was passed
                code = LANGCODES[to_language]
            elif to_language in LANGUAGES: # if code was passed
                code = to_language

            trans = Translator()
            translated_intro = trans.translate(intro_text, dest=code)
            await ctx.send(translated_intro.text)

        except:
            await ctx.send("Please enter a valid language!" +
            "\nUsage: ```pepe giveintro <language-name>```" +
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
    async def clear(self, ctx, user: typing.Optional[discord.Member] = None, number: typing.Optional[int] = 1):
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
            code = None
            if to_language in LANGCODES.keys(): # if language name was passed
                # print("lang name was passed!!")
                code = LANGCODES[to_language]
            elif to_language in LANGCODES.values(): # if code was passed
                # print("lang code was passed!!")
                code = to_language
            else:
                await ctx.send("Please enter a valid language!" +
                "\nUsage: ```pepe translate <text> <language-name>```" +
                "\nFor a list of supported languages, use \"pepe languages\"")

            # print(f"Text to be translated: \"{text}\", type: {type(code)}")
            # print(f"Recognized code: {code}, type: {type(code)}")
            # print(f"to_language: {to_language}, type: {type(code)}")

            trans = Translator()
            translated_text = trans.translate(text, dest=code)
            await ctx.send(translated_text.text)#, tts=True)
        except:
            traceback.print_exc()

    @commands.command(
    pass_context=True,
    name = 'scores',
    help = "Shows scores of all members in server!",
    usage = "pepe scores [@optional_user_mention]"
    )
    async def scores (self, ctx, mentioned_user: typing.Optional[discord.Member] = None):
        output = []

        conn = await init_db()
        results = None
        if mentioned_user is None:
            results = await conn.fetch("SELECT * FROM pepepig_users WHERE server_id=$1 ORDER BY score DESC", ctx.guild.id)
        else:
            results = await conn.fetch("SELECT * FROM pepepig_users WHERE member_id=$1 AND server_id=$2 ORDER BY score DESC", mentioned_user.id, ctx.guild.id)
        
        output.append("{:<30}{:<30}\n".format("User", "Score"))
        for i, record in enumerate(results):
            user = ctx.guild.get_member(record['member_id'])
            if user is not None:
                output.append("{:<30}{:<30}".format(user.display_name, record['score']))
            else:
                print(f"pepe.get_user() failed! (member_id = {record['member_id']} and server id = {ctx.guild.id}")

        await ctx.send('```\n' + '\n'.join(output) + '```')
        await conn.close()

    @commands.command(
    pass_context=True,
    name = 'emojify',
    help = "Emojifies the given text",
    usage = "pepe emojify <text to emojify>"
    )
    async def emojify(self, ctx):
        text = ctx.message.content.split()[2:]

        if text:
            # emoji_url = request.urlopen("http://erikyangs.com/emojipastagenerator/emojiMapping.json")
            # personal_emoji_url = request.urlopen("http://erikyangs.com/emojipastagenerator/personalEmojiMapping.json")

            with open("emojiMapping.json", encoding="utf8") as emoji_mapping_file, open("personalEmojiMapping.json", encoding="utf8") as personal_mapping_file:
                emoji_mapping = json.load(emoji_mapping_file)
                personal_mapping = json.load(personal_mapping_file)
                
                output = ""
                i = 0
                while i < len(text):
                    word = text[i]
                    nextword = text[i+1] if i < len(text)-1 else ""

                    if word.lower() in personal_mapping: # single word personal emoji match
                        output += (word + " " + personal_mapping[word.lower()] + " ")
                        i += 1
                    elif (word.lower() + " " + nextword.lower()) in personal_mapping: # double word personal emoji match 
                        #! THERE HAS TO BE A BETTER WAY TO DO THIS
                        output += (word + " " + nextword + " " + personal_mapping[word.lower() + " " + nextword.lower()] + " ")
                        i += 2
                    elif word.lower() in emoji_mapping: # emoji match
                        output += (word + " " + emoji_mapping[word.lower()] + " ")
                        i += 1
                    else: # no match at all. Just output the word
                        output += (word + " ")
                        i += 1
                await ctx.send(output)
        else:
            await ctx.send("Usage: ```pepe emojify <text to emojify>```")

def setup(pepe):
    pepe.remove_command('help')
    pepe.add_cog(PepeTasks(pepe))
    pepe.add_cog(UtilityCommands(pepe))
    pepe.add_cog(HelpCog(pepe))

setup(pepe)
pepe.run(TOKEN)