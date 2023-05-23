from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context

class Help(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command(description="Get some help.")
    async def help(self, ctx: Context):
        embed = Embed(title="BoxCat's Help")
        for command in self.bot.walk_commands():
            description = command.description
            if not description or description is None or description == "":
                description = "No Description Provided."
            embed.add_field(name=f"`${command.name}{(' ' + command.signature) if command.signature is not None else ''}`", value=description, inline=False)
        await ctx.send(embed=embed)
