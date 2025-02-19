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

        # print(f"Message from {ctx.author}: {ctx.content}")
        if await check_spiral_abyss_reset(ctx):
            return

        await bot.process_commands(ctx)

    for cogs in all_cogs:
        bot.add_cog(cogs(bot))

    bot.run(config["DISCORD_TOKEN"])

async def check_spiral_abyss_reset(ctx):
    if ("today" in ctx.content or "reset" in ctx.content) and "?" in ctx.content:
        MOC_RESET_DATE = datetime.date(2024, 11, 25)
        PF_RESET_DATE = datetime.date(2024, 11, 11)
        APC_RESET_DATE = datetime.date(2024, 10, 28)
        todayDate = datetime.datetime.today()
        abyss_reset = todayDate.day == 16
        it_reset = todayDate.day == 1
        moc_reset = (todayDate.date() - MOC_RESET_DATE).days % 42 == 0
        pf_reset = (todayDate.date() - PF_RESET_DATE).days % 42 == 0
        apc_reset = (todayDate.date() - APC_RESET_DATE).days % 42 == 0
        after_four_am = todayDate.time() >= datetime.time(4, 0, 0)

        stuff_reset = []

        if abyss_reset:
            stuff_reset.append("Spiral Abyss")
        if it_reset:
            stuff_reset.append("Imaginarium Theatre")
        if moc_reset:
            stuff_reset.append("Memory of Chaos")
        if pf_reset:
            stuff_reset.append("Pure Fiction")
        if apc_reset:
            stuff_reset.append("Apocalyptic Shadow")
        if abyss_reset or it_reset:
            stuff_reset.append("Shiyu Defense")

        if len(stuff_reset) == 0:
            await ctx.reply(f"It's not Spiral Abyss, Imaginarium Theatre, Apocalyptic Shadow, Pure Fiction, Memory of Chaos or Shiyu Defense reset day yet! {KIRARA_COOKIE}")
        elif not after_four_am:
            await ctx.reply(f"It\'s {' & '.join(stuff_reset)} reset day today, but it is not time yet! {KIRARA_COOKIE}")
        else:
            await ctx.reply(f"**It\'s {' & '.join(stuff_reset)} reset day today** {KIRARA_COOKIE}")            
        return True
    return False


if __name__ == "__main__":
    launch_discord()
