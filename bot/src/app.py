import asyncio
import os
import nextcord
from nextcord.ext import commands

from database import db_session

def launch():
    bot = commands.Bot(command_prefix='$')
    bot.remove_command('help')
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        await bot.change_presence(activity=nextcord.Activity(name="the cookie jar", type=nextcord.ActivityType.listening))

    bot.run(config["DISCORD_TOKEN"])


if __name__ == "__main__":
    launch()