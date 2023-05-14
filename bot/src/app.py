import asyncio
from dotenv import dotenv_values
import os
import nextcord
from nextcord.ext import commands

from cogs import all_cogs
from database import db_session

config = dotenv_values(".env")

"""Create bot object"""
intents = nextcord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='$', intents=intents)

def launch():
    bot.remove_command('help')
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        await bot.change_presence(activity=nextcord.Activity(name="to changes", type=nextcord.ActivityType.listening))
    
    for cogs in all_cogs:
        bot.add_cog(cogs(bot))

    bot.run(config["DISCORD_TOKEN"])


if __name__ == "__main__":
    launch()