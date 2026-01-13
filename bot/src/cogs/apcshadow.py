import genshin as gs
from genshin.models import StarRailAPCShadow
from nextcord import Embed, Colour
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from nextcord.ui import button, View
import traceback
from util import get_starrail_acc_by_name, get_starrail_acc_by_discord_id, hoyolab_client_init
from models import HoyolabAccount

'''All emotes used in this cog'''
MOC_STAR = "<:mocstar:1116273875018317914>"
PAGE_SIZE = 3

def strip(name_str):
     name_str = name_str.replace("<unbreak>", "")
     name_str = name_str.replace("</unbreak>", "")
     return name_str

'''Cog which contains all commands for showing Apocalyptic Shadow information.'''
class ApcShadow(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Shows details about the current Apocalyptic Shadow cycle clear.")
    async def apcshadow(self, ctx: Context, name: str=None, prev: str=None):
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

        '''Then, grab the data for as clears'''
        apcshadow = await self.get_as(account, prevFlag)
        as_floors = list(filter(lambda x: len(x.node_1.avatars) > 0, apcshadow.floors))
        embed = Embed(
            title=f"Apocalyptic Shadow stats for {account.name}",
            colour=Colour.brand_green(),
        )

        desc = "Total battles: {} | Total stars: {}\n".format(apcshadow.total_battles, apcshadow.total_stars)

        if len(as_floors) == 0:
            desc += f'{account.name} has not attempted Apocalyptic Shadow yet!'
        else:
            desc += f'Best stage: {strip(apcshadow.floors[0].name)}'
            details = ""
            first_team = ""
            second_team = ""

            for floor in as_floors:
                total_score = floor.node_1.score + floor.node_2.score
                details += f"{strip(' '.join(floor.name.split(' ')[-2:]))}\n{floor.star_num} {MOC_STAR}\nFirst Half: {floor.node_1.score}\nSecond Half: {floor.node_2.score}\nTotal score: {total_score}\n\n"
                first_team += f"**Buff**: { 'No buff' if floor.node_1.buff is None else floor.node_1.buff.name }\n"
                first_team += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_1.avatars) + "\n\n"
                second_team += f"**Buff**: { 'No buff' if floor.node_2.buff is None else floor.node_2.buff.name }\n"
                second_team += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_2.avatars) + "\n\n"
            embed.add_field(name='Stage', value=details)
            embed.add_field(name='1st team', value=first_team)
            embed.add_field(name='2nd team', value=second_team)

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

    async def get_as(self, account: HoyolabAccount, prevFlag) -> StarRailAPCShadow:
        client = hoyolab_client_init(account, gs.Game.STARRAIL)
        return await client.get_starrail_apc_shadow(uid=account.starrail_uid, previous=prevFlag)
