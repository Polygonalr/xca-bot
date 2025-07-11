import genshin as gs
from genshin.models import ShiyuDefense
from nextcord import Embed, Colour
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from nextcord.ui import button, View
import traceback
from util import hoyolab_client_init, get_zzz_acc_by_name, get_zzz_acc_by_discord_id
from models import HoyolabAccount

'''All emotes used in this cog'''
DA_STAR = "<:da_star:1366019752668958728>"

'''Cog which contains all commands for showing Deadly Assault information.'''
class DeadlyAssault(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['da'], description="Shows details about the current Deadly Assault cycle clear.")
    async def deadlyassault(self, ctx: Context, name: str=None, prev: str=None):
        '''Initialisation and checks'''
        prevFlag = False
        account = get_zzz_acc_by_discord_id(ctx.author.id) if name in [None, "prev"] else get_zzz_acc_by_name(name)
        if name == "prev" or prev == "prev":
            prevFlag = True

        if account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Zenless Zone Zero account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        '''Checks should be all ok by here, proceed with data retrieval'''
        '''First, need to grab character names and their corresponding ids'''
        char_names = await self.get_characters(account)
        bangboo_names = await self.get_bangboos(account)
        
        embed = Embed(
            title=f"Deadly Assault stats for {account.name}",
            colour=Colour.brand_green(),
        )
        desc = ""

        '''Then, grab the data for DA clears'''
        da: DeadlyAssault = await self.get_da(account, prevFlag)
        if not da.has_data:
            desc += f'{account.name} has not attempted Deadly Assault yet!'
        else:
            desc += f'Score: {da.total_score} | Stars: {da.total_star} | Ranking: {da.rank_percent}'
            if len(da.challenges) == 0:
                desc += f'\nFull challenge data is not available yet!'
            else:
                for challenge in da.challenges:
                    field_name = f"{challenge.boss.name}"
                    field_val = f"Score: **{challenge.score}** {DA_STAR * challenge.star}\n"
                    field_val += f"Buff: **{challenge.buffs[0].name}**\n"
                    field_val += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in challenge.agents)
                    field_val += f"\n{bangboo_names[challenge.bangboo.id]} (lvl {challenge.bangboo.level})"
                    embed.add_field(name=field_name, value=field_val)

        embed.description = desc
        await ctx.reply(embed=embed)
    
    # TODO cache the id to name mapping
    async def get_characters(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        characters = await client.get_zzz_agents(uid=account.zzz_uid)
        mapping = {}
        for character in characters:
            mapping[character.id] = character.name
        return mapping

    async def get_bangboos(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        bangboos = await client.get_bangboos(uid=account.zzz_uid)
        mapping = {}
        for bangboo in bangboos:
            mapping[bangboo.id] = bangboo.name
        return mapping

    async def get_da(self, account: HoyolabAccount, prevFlag):
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        return await client.get_deadly_assault(uid=account.zzz_uid, previous=prevFlag)
