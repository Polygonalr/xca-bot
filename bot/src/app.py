import asyncio
import datetime
from dotenv import dotenv_values
import os
import nextcord
from nextcord.ext import commands

from cogs import all_cogs
from database import init_db

config = dotenv_values(".env")
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"

'''Create bot object'''
intents = nextcord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

def launch():
    init_db()
    bot.remove_command('help')
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        await bot.change_presence(activity=nextcord.Activity(name="changes", type=nextcord.ActivityType.listening))
    
    @bot.event
    async def on_message(ctx):
        if ctx.author == bot.user:
            return

        print(f"Message from {ctx.author}: {ctx.content}")
        if await check_spiral_abyss_reset(ctx):
            return

        await bot.process_commands(ctx)

    for cogs in all_cogs:
        bot.add_cog(cogs(bot))

    bot.run(config["DISCORD_TOKEN"])

async def check_spiral_abyss_reset(ctx):
    # check whether it's 1st or 16th of the month
    todayDate = datetime.date.today()
    if ("today" in ctx.content or "reset" in ctx.content) and "?" in ctx.content:
        if todayDate.day in [1, 16]:
            await ctx.reply(f"**It's spiral abyss & memory of chaos reset day today** {KIRARA_COOKIE}")
        else:
            await ctx.reply(f"It's not spiral abyss & memory of chaos reset day today {KIRARA_COOKIE}")
        return True
    return False


if __name__ == "__main__":
    launch()