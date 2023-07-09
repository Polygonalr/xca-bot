import genshin as gs
from genshin.models import StarRailRogue
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from util import get_starrail_acc_by_name, get_starrail_acc_by_discord_id
from models import HoyolabAccount

class Simu(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command(description="Show how many Simulated Universes you have cleared this week.")
    async def simu(self, ctx: Context, name: str=None):
        account = get_starrail_acc_by_name(name) if name is not None else get_starrail_acc_by_discord_id(ctx.author.id)
        if account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Star Rail account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return
        
        simu = await self.get_simu(account)
        embed = Embed(
            description=f"You have cleared **{simu.current_record.basic.finish_cnt}** Simulated Universes this week.",
            colour=Colour.brand_green(),
        )
        await ctx.reply(embed=embed)

    async def get_simu(self, account: HoyolabAccount) -> StarRailRogue:
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_starrail_rogue(uid=account.starrail_uid)