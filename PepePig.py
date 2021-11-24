# bot.py
import json
import os
import random
import re
import sys
import traceback
import typing

import asyncpg
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from googletrans import LANGCODES, LANGUAGES, Translator

isLocal = False

# To make local dev easier, we can use dotenv to load environment variables from a .env file
# If the --local argument is NOT passed, we will use the environment variables from the Heroku environment
if sys.argv[1] == "--local":
    isLocal = True
    load_dotenv()
toAdd = "Yes, LOCAL\n" if isLocal else ""

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

pepe = commands.Bot(
    command_prefix=["pepe ", "Pepe "],
    # help_command=None,
    description="I'm a pretty useless bot made by @rishee#8641",
    intents=intents,
)


@pepe.event
async def on_ready():
    print(f"{pepe.user} has connected to Discord!")
    game = discord.Game(name="VALORANT")
    await pepe.change_presence(activity=game)


async def init_db() -> asyncpg.connection.Connection:
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS pepepig_users (
            s_no SERIAL PRIMARY KEY, 
            member_id bigint, 
            score bigint,
            server_id bigint
        )
    """
    )
    # print("Create table if not exists done.")
    return conn


@pepe.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.channel.send(
            "That's not a valid command! Type `pepe help` to get a list of commands."
        )


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

        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM pepepig_users WHERE member_id=$1 AND server_id=$2)",
            author_id,
            guild_id,
        )
        # print(f"Does user {message.author} exist in db? [{exists}]")

        increment_val = random.randint(20, 50)

        if exists:
            new_score = await conn.fetchval(
                "UPDATE pepepig_users SET score=score+$1 WHERE member_id=$2 AND server_id=$3 RETURNING score",
                increment_val,
                author_id,
                guild_id,
            )
            # print(f"User already has a score in this server! New score for {message.author.display_name} = {new_score}")
        else:
            new_score = await conn.fetchval(
                "INSERT INTO pepepig_users (member_id, score, server_id) VALUES ($1, $2, $3) RETURNING score",
                author_id,
                increment_val,
                guild_id,
            )
            # print(f"New user entry for this server! New score for {message.author.display_name} = {new_score}")
        await conn.close()
    except Exception as e:
        print(e)
        print("\nCOULDN'T CONNECT TO DATABASE!")

    msg = message.content
    # ? Call the rest of the stuff only if not an attempt to use the bot
    prefixes = await pepe.get_prefix(message)
    if (
        isinstance(prefixes, list)
        and list(filter(lambda x: msg.startswith(x), prefixes))
        or isinstance(prefixes, str)
        and msg.startswith(prefixes)
    ):
        await pepe.process_commands(message)
    # ? ayy -> lmao
    elif msg.lower().startswith("ayy") and msg.lower().endswith("y"):
        await message.channel.send(f"lmao {message.author.mention}")
    # ? Easter egg (?)
    elif "who" in msg.lower() and "daddy" in msg.lower():
        Rishi = pepe.get_user(425968693424685056)
        await message.channel.send(f"{Rishi.mention} is my daddy.")
    # ? For reporting bruh moment
    elif bool(re.match(r"[b]+[r]+[u]+[h]+", msg, re.IGNORECASE)):
        img = discord.File(
            open("media/satsriakal bruh.jpg", "rb"), filename="satsriakal.jpg"
        )
        await message.channel.send(file=img)
        await message.channel.send(
            f"**Bruh moment successfully reported by {message.author.mention}**"
        )
    # For valo
    elif (
        re.search(r"(valo(rant)?[?]?[\s]?[\$]?)", msg, re.IGNORECASE)
        or "<@&763655495285473300>" in msg.lower()
    ):
        await message.channel.send(f"{message.author.mention} haan ruk bro mai aara")


class MyHelpCommand(commands.DefaultHelpCommand):
    def get_command_signature(self, command):
        return "{0.clean_prefix}{1.qualified_name} - {1.signature}".format(
            self, command
        )

    @commands.command(name="help", hidden=True)
    async def help(self, ctx):
        await ctx.send("HELP SCREEN")


class HelpCog(
    commands.Cog,
    command_attrs=dict(name="Help", usage="pepe help <optional category>", hidden=True),
):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


class PepeTasks(commands.Cog):
    """
    Contains first year tasks.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        pass_context=True,
        name="giveintro",
        help="Gives intro in various languages.",
        usage="pepe giveintro <language-name>",
    )
    async def giveintro(self, ctx):
        msg = ctx.message
        words = msg.content.split()
        to_language = words[-1]  # pepe giveintro <langauge>

        intro_text = "I'm Pepe Pig (**cRoaK**).\nThis is my little brother George (**mEeP mEeP**),\nthis is mummy pig (**bruh sound effect #2**),\nand this is DADDY FROG (**huge snort**)"

        # LANGCODES has keys as languages, values as codes
        try:
            # LANGCODES has keys as languages, values as codes
            # LANGUAGES has keys as codes, values as languages
            code = "en"
            if to_language in LANGCODES:  # if language name was passed
                code = LANGCODES[to_language]
            elif to_language in LANGUAGES:  # if code was passed
                code = to_language

            trans = Translator()
            translated_intro = trans.translate(intro_text, dest=code)
            await ctx.send(toAdd + translated_intro.text)

        except:
            await ctx.send(
                toAdd
                + "Please enter a valid language!"
                + "\nUsage: ```pepe giveintro <language-name>```"
                + '\nFor a list of supported languages, use "pepe languages"'
            )


class UtilityCommands(commands.Cog):
    """
    Contains some useful commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        pass_context=True,
        name="languages",
        help="Lists all supported languages for translation",
    )
    async def languages(self, ctx):
        text = [(lang, code) for lang, code in LANGCODES.items()]
        await ctx.send("\n".join([f"{code}: {lang}" for code, lang in text]))

    @commands.command(
        pass_context=True,
        name="clear",
        help="Clears the n most recent messages from specific/all users",
    )
    async def clear(
        self,
        ctx,
        user: typing.Optional[discord.Member] = None,
        number: typing.Optional[int] = 1,
    ):
        if user is None:
            deleted = await ctx.channel.purge(limit=number + 1)
            await ctx.send(
                "{} deleted the last {} message(s) lol. Ab tu suspense me hi mar".format(
                    ctx.message.author.name, number
                )
            )
        else:
            count = 0
            to_delete = []

            if user.id == ctx.message.author.id:
                number += 1

            async for message in ctx.channel.history():  # default limit 100
                if count == number:
                    break
                if message.author.id == user.id:
                    to_delete.append(message)
                    count += 1

            await ctx.channel.delete_messages(to_delete)
            await ctx.send(
                "{} deleted the last {} message(s) from user {}.".format(
                    ctx.message.author.name, number, user.display_name
                )
            )

    @commands.command(
        pass_context=True,
        name="translate",
        help="Translates from detected language to whatever language you want!",
        usage="pepe translate <text IN QUOTES> <destination-language>",
    )
    async def translate(self, ctx):
        msg = ctx.message
        words = msg.content.split()
        to_language = words[-1].lower()
        text = str()

        arr = msg.content.split('"')
        if len(arr) == 3:
            text = arr[1]
        else:
            text = " ".join(words[2:-1])

        try:
            # LANGCODES has keys as languages, values as codes
            # LANGUAGES has keys as codes, values as languages
            code = None
            if to_language in LANGCODES.keys():  # if language name was passed
                # print("lang name was passed!!")
                code = LANGCODES[to_language]
            elif to_language in LANGCODES.values():  # if code was passed
                # print("lang code was passed!!")
                code = to_language
            else:
                await ctx.send(
                    toAdd
                    + "Please enter a valid language!"
                    + "\nUsage: ```pepe translate <text> <language-name>```"
                    + '\nFor a list of supported languages, use "pepe languages"'
                )
                return

            trans = Translator()
            translated_text = trans.translate(text, dest=code)
            await ctx.send(toAdd + translated_text.text)  # , tts=True)
        except:
            traceback.print_exc()

    @commands.command(
        pass_context=True,
        name="scores",
        help="Shows scores of all members in server!",
        usage="pepe scores [@optional_user_mention]",
    )
    async def scores(self, ctx, mentioned_user: typing.Optional[discord.Member] = None):
        output = []

        conn = await init_db()
        results = None
        if mentioned_user is None:
            results = await conn.fetch(
                "SELECT * FROM pepepig_users WHERE server_id=$1 ORDER BY score DESC",
                ctx.guild.id,
            )
        else:
            results = await conn.fetch(
                "SELECT * FROM pepepig_users WHERE member_id=$1 AND server_id=$2 ORDER BY score DESC",
                mentioned_user.id,
                ctx.guild.id,
            )

        output.append("{:<30}{:<30}\n".format("User", "Score"))
        for i, record in enumerate(results):
            user = ctx.guild.get_member(record["member_id"])
            if user is not None:
                output.append("{:<30}{:<30}".format(user.display_name, record["score"]))
            else:
                # ? if here, it just means that the user isn't in the server anymore
                pass

        await ctx.send(toAdd + "```\n" + "\n".join(output) + "```")
        await conn.close()

    @commands.command(
        pass_context=True,
        name="emojify",
        help="Emojifies the given text",
        usage="pepe emojify <text to emojify>",
    )
    async def emojify(self, ctx):
        # ? Strip first 2 words from message which are "pepe" and "emojify"
        text = ctx.message.content.split()[2:]
        # print(f"Type of input text = {type(text)}")
        # print(f"Input text = {text}")

        trans = Translator()

        # ? personal emoji match
        def case1():
            return word + " " + personal_mapping[word.lower()] + " "

        # ? translated personal emoji match
        def case2():
            return word + " " + personal_mapping[translated_word.lower()] + " "

        # ? emoji match
        def case3():
            return word + " " + emoji_mapping[word.lower()] + " "

        # ? translated emoji match
        def case4():
            return word + " " + emoji_mapping[translated_word.lower()] + " "

        # ? no match at all. Just add a random emoji with the word
        def case5():
            return (
                word + " " + random.choice(personal_mapping["random_emojis_list"]) + " "
            )

        if text:
            # emoji_url = request.urlopen("http://erikyangs.com/emojipastagenerator/emojiMapping.json")
            # personal_emoji_url = request.urlopen("http://erikyangs.com/emojipastagenerator/personalEmojiMapping.json")
            with open("emojiMapping.json", encoding="utf8") as emoji_mapping_file, open(
                "personalEmojiMapping.json", encoding="utf8"
            ) as personal_mapping_file:
                emoji_mapping = json.load(emoji_mapping_file)
                personal_mapping = json.load(personal_mapping_file)
                output = ""
                for i, word in enumerate(text):
                    translated_word = trans.translate(word, dest="en").text
                    # print(
                    #     f"i = {i}/{len(text)}, word: {word}, translated word: {translated_word}"
                    # )

                    if word.isdigit():
                        for digit in word:
                            output += personal_mapping[digit] + " "  # ; print("case0")
                        continue
                    elif word.lower() == "ok":
                        output += personal_mapping[word.lower()] + " "
                        continue

                    # ? try all funcs in order, stop at first non-error-throwing function
                    for func in [case1, case2, case3, case4, case5]:
                        try:
                            output += func()
                            # print(
                            #     f"Found {word} or {translated_word}, in case:",
                            #     func.__name__,
                            # )
                            break
                        except Exception as e:
                            pass
                await ctx.send(toAdd + output)
        else:
            await ctx.send("Usage: ```pepe emojify <text to emojify>```")


def setup(pepe):
    # pepe.remove_command("help")
    pepe.add_cog(PepeTasks(pepe))
    pepe.add_cog(UtilityCommands(pepe))
    # pepe.add_cog(HelpCog(pepe))


setup(pepe)
pepe.run(TOKEN)
