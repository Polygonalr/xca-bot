import genshin as gs
from genshin.models import ShiyuDefense
from nextcord import Embed, Colour
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from nextcord.ui import button, View
import datetime
import traceback
from util import hoyolab_client_init, get_zzz_acc_by_name, get_zzz_acc_by_discord_id
from models import HoyolabAccount

'''All emotes used in this cog'''
S_RANK = "<:SRank:1269525641636614257>"
A_RANK = "<:ARank:1269525637400367206>"
B_RANK = "<:BRank:1269525639816417301>"
RANK_DICT = {'S': f"{S_RANK}", 'A': f"{A_RANK}", 'B': f"{B_RANK}"}

PAGE_SIZE = 3

def render_embed(acc_name: str, data: ShiyuDefense, char_names: dict, bangboo_names: dict, page: int=0) -> Embed:
    desc = ' | '.join(f"{RANK_DICT[x]}: {data.ratings.get(x, 0)}" for x in ['S', 'A', 'B']) + "\n"
    floors = list(filter(lambda x: len(x.node_1.characters) > 0, data.floors))

    embed = Embed(
        title=f"Shiyu Defense (Critical) stats for {acc_name}",
        colour=Colour.brand_green(),
    )
    stages_to_show = min(PAGE_SIZE, len(floors))
    if stages_to_show == 0:
        desc += f'{acc_name} has not attempted Shiyu Defense (Critical) yet!'
    else:
        desc += f'Best stage: {floors[0].name}'
        desc += f'\nTotal battle time: {str(datetime.timedelta(seconds=data.total_clear_time()))}'
        details = ""
        firstteam = ""
        secondteam = ""

        for floor in floors[page*PAGE_SIZE:page*PAGE_SIZE+stages_to_show]:
            details += f"{' '.join(floor.name.split(' ')[-2:])}\n1st half: {str(floor.node_1.battle_time)}\n2nd half: {str(floor.node_2.battle_time)}\n{RANK_DICT[floor.rating]}\n\n"
            firstteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_1.characters) + "\n"
            firstteam += f"{bangboo_names[floor.node_1.bangboo.id]} (lvl {floor.node_1.bangboo.level})\n\n"
            secondteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_2.characters) + "\n"
            secondteam += f"{bangboo_names[floor.node_2.bangboo.id]} (lvl {floor.node_2.bangboo.level})\n\n"
        embed.add_field(name='Stage', value=details)
        embed.add_field(name='1st team', value=firstteam)
        embed.add_field(name='2nd team', value=secondteam)
    
    embed.description = desc
    return embed

class ShiyuView(View):
    def __init__(self, acc_name: str, data: ShiyuDefense, char_names: dict, bangboo_names: dict, page: int=0):
        self.page = 0
        self.acc_name = acc_name
        self.data = data
        self.char_names = char_names
        self.bangboo_names = bangboo_names
        super().__init__(timeout=None)
    
    def number_of_pages(self) -> int:
        num_floors = len(list(filter(lambda x: len(x.node_1.characters) > 0, self.data.floors)))
        return (num_floors + PAGE_SIZE - 1) // PAGE_SIZE
    
    @button(label="", custom_id="shiyu-prev", style=1, emoji="⬅️")
    async def prev_callback(self, button, interaction: Interaction):
        if self.page - 1 < 0:
            await interaction.response.send_message("You are already at the first page!", ephemeral=True)
            return
        self.page -= 1
        if self.page - 1 < 0:
            self.prev_callback.disabled = True
        if self.page + 1 < self.number_of_pages():
            self.next_callback.disabled = False
        embed = render_embed(self.acc_name, self.data, self.char_names, self.bangboo_names, self.page)
        await interaction.message.edit(embed=embed, view=self)
    
    @button(label="", custom_id="shiyu-next", style=1, emoji="➡️")
    async def next_callback(self, button, interaction):
        if self.page + 1 >= self.number_of_pages():
            await interaction.response.send_message("You are already at the last page!", ephemeral=True)
            return
        self.page += 1
        if self.page + 1 >= self.number_of_pages():
            self.next_callback.disabled = True
        if self.page - 1 >= 0:
            self.prev_callback.disabled = False
        embed = render_embed(self.acc_name, self.data, self.char_names, self.bangboo_names, self.page)
        await interaction.message.edit(embed=embed, view=self)

'''Cog which contains all commands for showing Shiyu Defense Critical information.'''
class Shiyu(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Shows details about the current Shiyu Defense Critical cycle clear.")
    async def shiyu(self, ctx: Context, name: str=None, prev: str=None):
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

        '''Then, grab the data for shiyu clears'''
        shiyu = await self.get_shiyu(account, prevFlag)
        embed = render_embed(account.name, shiyu, char_names, bangboo_names)
        view = ShiyuView(acc_name=account.name, data=shiyu, char_names=char_names, bangboo_names=bangboo_names)
        view.prev_callback.disabled = True

        await ctx.reply(embed=embed, view=view)
    
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

    async def get_shiyu(self, account: HoyolabAccount, prevFlag):
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        return await client.get_shiyu_defense(uid=account.zzz_uid, previous=prevFlag)
