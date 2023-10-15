from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from util import get_genshin_acc_by_discord_id, get_genshin_acc_by_name, get_starrail_acc_by_discord_id, get_starrail_acc_by_name

ENKA_GENSHIN = "https://enka.network/u/"
ENKA_HSR = "https://enka.network/hsr/"

'''Cog to generate Enka links. TODO render enka character sheets in the future.'''
class Enka(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Lists down every Hoyolab account under my control.")
    async def enka(self, ctx: Context, name: str=None):
        if name == None: # Retrieve data for the sender
            genshin_account = get_genshin_acc_by_discord_id(ctx.author.id)
            hsr_account = get_starrail_acc_by_discord_id(ctx.author.id)
        else:
            genshin_account = get_genshin_acc_by_name(name)
            hsr_account = get_starrail_acc_by_name(name)

        if genshin_account == None and hsr_account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin & Star Rail account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        name = genshin_account.name if genshin_account != None else hsr_account.name
        embed = Embed(
            title=f"Enka link(s) for {name}",
            colour=Colour.brand_green(),
        )
        if genshin_account != None:
            embed.add_field(name="Genshin Impact", value=ENKA_GENSHIN + str(genshin_account.genshin_uid))
        if hsr_account.starrail_uid != None:
            embed.add_field(name="Honkai: Star Rail", value=ENKA_HSR + str(hsr_account.starrail_uid))
        
        await ctx.reply(embed=embed)
