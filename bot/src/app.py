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
        MOC_RESET_DATE = datetime.date(2023, 12, 25)
        PF_RESET_DATE = datetime.date(2024, 1, 8)
        todayDate = datetime.datetime.today()
        abyss_reset = todayDate.day in [1, 16]
        moc_reset = (todayDate.date() - MOC_RESET_DATE).days % 28 == 0
        pf_reset = (todayDate.date() - PF_RESET_DATE).days % 28 == 0
        after_four_am = todayDate.time() >= datetime.time(4, 0, 0)
        if abyss_reset:
            extra_text = ""
            if moc_reset:
                extra_text = " & Memory of Chaos"
            elif pf_reset:
                extra_text = " & Pure Fiction"
            if not after_four_am:
                await ctx.reply(f"It's Spiral Abyss{extra_text} reset day today, but it is not time yet! {KIRARA_COOKIE}")
            else:
                await ctx.reply(f"**It's Spiral Abyss{extra_text} reset day today** {KIRARA_COOKIE}")
        elif moc_reset:
            if not after_four_am:
                await ctx.reply(f"It's Memory of Chaos reset today, but it is not time yet! {KIRARA_COOKIE}")
            else:
                await ctx.reply(f"**It's Memory of Chaos reset today** {KIRARA_COOKIE}")
        elif pf_reset:
            if not after_four_am:
                await ctx.reply(f"It's Pure Fiction reset today, but it is not time yet! {KIRARA_COOKIE}")
            else:
                await ctx.reply(f"**It's Pure Fiction reset today** {KIRARA_COOKIE}")
        else:
            await ctx.reply(f"It's not Spiral Abyss, Memory of Chaos or Pure Fiction reset day yet! {KIRARA_COOKIE}")
        return True
    return False


if __name__ == "__main__":
    launch_discord()
