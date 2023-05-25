from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from util import get_all_genshin_accounts, get_all_starrail_accounts

'''Cog with command to list down all Hoyolab accounts that the bot has access to.'''
class List(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Lists down every Hoyolab account under my control.")
    async def list(self, ctx: Context):
        embed = Embed(
            title="Displaying every account under my control",
            colour=Colour.brand_green(),
        )

        '''Genshin accounts'''
        accs = get_all_genshin_accounts()
        genshin_names = [acc.name for acc in accs]
        embed.add_field(name="Genshin Acc", value="\n".join(genshin_names), inline=True)
        genshin_uids = [str(acc.genshin_uid) for acc in accs]
        embed.add_field(name="uids", value="\n".join(genshin_uids), inline=True)

        embed.add_field(name = chr(173), value = chr(173))

        '''Starrail Accounts'''
        accs = get_all_starrail_accounts()
        starrail_names = [acc.name for acc in accs]
        embed.add_field(name="Starrail Acc", value="\n".join(starrail_names), inline=True)
        starrail_uids = [str(acc.starrail_uid) for acc in accs]
        embed.add_field(name="uids", value="\n".join(starrail_uids), inline=True)

        embed.add_field(name = chr(173), value = chr(173))

        await ctx.reply(embed=embed)
