import genshin as gs
from genshin.models import AnomalyArbitration
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from util import get_starrail_acc_by_name, get_starrail_acc_by_discord_id, hoyolab_client_init
from models import HoyolabAccount

'''All emotes used in this cog'''
MOC_STAR = "<:mocstar:1116273875018317914>"
PAGE_SIZE = 3

def strip(name_str):
     name_str = name_str.replace("<unbreak>", "")
     name_str = name_str.replace("</unbreak>", "")
     return name_str

'''Cog which contains all commands for showing Anomaly Arbitration information.'''
class Arbitration(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Shows details about the current Anomaly Arbitration cycle clear.", aliases=["aa"])
    async def arbitration(self, ctx: Context, name: str=None, prev: str=None):
        '''Initialisation and checks'''
        prevFlag = False
        account = get_starrail_acc_by_discord_id(ctx.author.id) if name in [None, "prev"] else get_starrail_acc_by_name(name)
        if name == "prev" or prev == "prev":
            prevFlag = True

        if account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Star Rail account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        '''Checks should be all ok by here, proceed with data retrieval'''
        '''First, need to grab character names and their corresponding ids'''
        char_names = await self.get_characters(account)

        '''Then, grab the data for aa clears'''
        arbitration = await self.get_aa(account, prevFlag)
        if len(arbitration.records) == 0:
            embed = Embed(
                description=f'Error: {account.name} did not complete Anomaly Arbitration before!',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        latest_cycle = arbitration.records[0]
        knight_records = latest_cycle.mini_boss_records
        king_record = latest_cycle.boss_record
        embed = Embed(
            title=f"Anomaly Arbitration stats for {account.name}",
            colour=Colour.brand_green(),
        )

        desc = "Total battles: {} | Knight stars: {} | King stars: {}\n".format(arbitration.summary.challenge_attempts, arbitration.summary.mini_boss_stars, arbitration.summary.boss_stars)

        if len(knight_records) == 0:
            desc += f'{account.name} has not attempted Anomaly Arbitration yet!'
        else:
            # Knights
            for i, knight in enumerate(knight_records):
                stage_desc = f"**Cycles**: {knight.cycles_used}\n"
                stage_desc += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in knight.characters)
                embed.add_field(name=f'Knight {i+1}', value=stage_desc)

            # King
            if king_record is not None:
                king_desc = f"**Cycles**: {king_record.cycles_used} | **Hard mode**: {'Yes' if king_record.is_hard_mode else 'No'}\n**Buff selected**: {king_record.buff.name}\n"
                king_desc += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in king_record.characters)
            else:
                king_desc = f"King was not attempted yet!"
            embed.add_field(name=f'King', value=king_desc)

        embed.description = desc
        await ctx.reply(embed=embed)
    
    # TODO cache the id to name mapping
    async def get_characters(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.STARRAIL)
        characters = await client.get_starrail_characters(uid=account.starrail_uid)
        mapping = {}
        for character in characters.avatar_list:
            mapping[character.id] = character.name
        for i in range (8000, 8021):
            mapping[i] = "Trailblazer"
        return mapping

    async def get_aa(self, account: HoyolabAccount, prevFlag) -> AnomalyArbitration:
        client = hoyolab_client_init(account, gs.Game.STARRAIL)
        return await client.get_anomaly_arbitration(uid=account.starrail_uid, previous=prevFlag)
