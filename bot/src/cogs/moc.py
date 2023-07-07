import genshin as gs
from genshin.models import StarRailChallenge
from nextcord import Embed, Colour
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from nextcord.ui import button, View
import traceback
from util import get_starrail_acc_by_name, get_starrail_acc_by_discord_id
from models import HoyolabAccount

'''All emotes used in this cog'''
MOC_STAR = "<:mocstar:1116273875018317914>"
PAGE_SIZE = 3

def render_embed(acc_name: str, data: StarRailChallenge, char_names: dict, page: int=0) -> Embed:
    desc = "Total battles: {} | Total stars: {}\n"\
        .format(data.total_battles, data.total_stars)
    floors = data.floors

    embed = Embed(
        title=f"Memory of Chaos stats for {acc_name}",
        colour=Colour.brand_green(),
    )
    stages_to_show = min(PAGE_SIZE, len(floors))
    if stages_to_show == 0:
        desc += f'{acc_name} has not attempted Memory of Chaos yet!'
    else:
        if stages_to_show == 1:
            desc += f'Showing stats for {floors[0].name}'
        else:
            desc += f'Showing stats for {floors[stages_to_show-1].name} to {" ".join(floors[0].name.split(" ")[-2:])}'
        details = ""
        firstteam = ""
        secondteam = ""

        for floor in floors[page*PAGE_SIZE:page*PAGE_SIZE+stages_to_show]:
            details += f"{' '.join(floor.name.split(' ')[-2:])}\n{floor.star_num} {MOC_STAR}\n{floor.round_num} cycles\n\n\n"
            firstteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_1.avatars) + "\n\n"
            secondteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_2.avatars) + "\n\n"
        embed.add_field(name='Stage', value=details)
        embed.add_field(name='1st team', value=firstteam)
        embed.add_field(name='2nd team', value=secondteam)
    
    embed.description = desc
    return embed

class MOCView(View):
    def __init__(self, acc_name: str, data: StarRailChallenge, char_names: dict, page: int=0):
        self.page = 0
        self.acc_name = acc_name
        self.data = data
        self.char_names = char_names
        super().__init__(timeout=None)
    
    def number_of_pages(self) -> int:
        return (len(self.data.floors) + PAGE_SIZE - 1) // PAGE_SIZE
    
    @button(label="", custom_id="moc-prev", style=1, emoji="⬅️")
    async def prev_callback(self, button, interaction: Interaction):
        if self.page - 1 < 0:
            await interaction.response.send_message("You are already at the first page!", ephemeral=True)
            return
        self.page -= 1
        embed = render_embed(self.acc_name, self.data, self.char_names, self.page)
        await interaction.message.edit(embed=embed, view=self)
    
    @button(label="", custom_id="moc-next", style=1, emoji="➡️")
    async def next_callback(self, button, interaction):
        if self.page + 1 >= self.number_of_pages():
            await interaction.response.send_message("You are already at the last page!", ephemeral=True)
            return
        self.page += 1
        embed = render_embed(self.acc_name, self.data, self.char_names, self.page)
        await interaction.message.edit(embed=embed, view=self)

'''Cog which contains all commands for showing Memory of Chaos information.'''
class MOC(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Shows details about the current Memory of Chaos cycle clear.")
    async def moc(self, ctx: Context, name: str=None, prev: str=None):
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

        '''Then, grab the data for moc clears'''
        moc = await self.get_moc(account, prevFlag)
        embed = render_embed(account.name, moc, char_names)

        await ctx.reply(embed=embed, view=MOCView(acc_name=account.name, data=moc, char_names=char_names))
    
    # TODO cache the id to name mapping
    async def get_characters(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        characters = await client.get_starrail_characters(uid=account.starrail_uid)
        mapping = {}
        for character in characters.avatar_list:
            mapping[character.id] = character.name
        return mapping

    async def get_moc(self, account: HoyolabAccount, prevFlag) -> StarRailChallenge:
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_starrail_challenge(uid=account.starrail_uid, previous=prevFlag)
