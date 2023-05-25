from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context

'''Cog for ping command.'''
class Ping(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: Context):
        await ctx.reply(f'Pong! {round(self.bot.latency * 1000)}ms')