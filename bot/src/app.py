import asyncio
import datetime
from dotenv import dotenv_values
import nextcord
from nextcord.ext import commands

from cogs import all_cogs
from util import get_all_discord_ids
from database import init_db

config = dotenv_values(".env")
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"

'''Create bot object'''
intents = nextcord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='$', intents=intents)

def launch_discord():
    init_db()
    bot.remove_command('help')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        await bot.change_presence(activity=nextcord.Activity(name="for new orders", type=nextcord.ActivityType.watching))
    
    @bot.event
    async def on_message(ctx):
        if ctx.author == bot.user or ctx.author.id not in get_all_discord_ids():
            return

        print(f"Message from {ctx.author}: {ctx.content}")
        if await check_spiral_abyss_reset(ctx):
            return

        await bot.process_commands(ctx)

    for cogs in all_cogs:
        bot.add_cog(cogs(bot))

    bot.run(config["DISCORD_TOKEN"])

async def check_spiral_abyss_reset(ctx):
    if ("today" in ctx.content or "reset" in ctx.content) and "?" in ctx.content:
        MOC_RESET_DATE = datetime.date(2023, 6, 26)
        todayDate = datetime.date.today()
        abyss_reset = todayDate.day in [1, 16]
        moc_reset = (todayDate - MOC_RESET_DATE).days % 14 == 0
        if abyss_reset and moc_reset:
            await ctx.reply(f"**It's spiral abyss & memory of chaos reset day today** {KIRARA_COOKIE}")
        elif abyss_reset:
            await ctx.reply(f"**It's spiral abyss reset day today** {KIRARA_COOKIE}")
        elif moc_reset:
            await ctx.reply(f"**It's memory of chaos reset day today** {KIRARA_COOKIE}")
        else:
            await ctx.reply(f"It's not spiral abyss & memory of chaos reset day today {KIRARA_COOKIE}")
        return True
    return False


if __name__ == "__main__":
    launch_discord()