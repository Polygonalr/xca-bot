import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from util import get_starrail_acc_by_name, get_starrail_acc_by_discord_id
from models import HoyolabAccount

'''All emotes used in this cog'''
MOC_STAR = "<:mocstar:1116273875018317914>"

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
        desc = "Total battles: {} | Best stage: {}\nTotal stars: {}\n"\
            .format(moc.total_battles, moc.max_floor, moc.total_stars)
        floors = moc.floors
        if prevFlag:
            embed = Embed(
                    title=f"Previous cycle MoC stats for {account.name}",
                    colour=Colour.brand_green(),
                    )
        else:
            embed = Embed(
                    title=f"Memory of Chaos stats for {account.name}",
                    colour=Colour.brand_green(),
                    )
            
        '''Format last 3 stages clear details'''
        stages_to_show = min(3, len(floors))
        if stages_to_show == 0:
            embed.description = f'{account.name} has not attempted Memory of Chaos yet!'
        else:
            if stages_to_show == 1:
                embed.description = f'Showing stats for {floors[0].name}'
            else:
                embed.description = f'Showing stats for {floors[stages_to_show-1].name} to {floors[0].name}'
            details = ""
            firstteam = ""
            secondteam = ""

            for floor in floors[:stages_to_show][::-1]:
                details += f"{floor.name}\n{floor.star_num} {MOC_STAR}\n{floor.round_num} cycles\n\n\n"
                firstteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_1.avatars) + "\n\n"
                secondteam += "\n".join(f"{char_names[x.id]} (lvl {x.level})" for x in floor.node_2.avatars) + "\n\n"
            embed.add_field(name='Stage', value=details)
            embed.add_field(name='1st team', value=firstteam)
            embed.add_field(name='2nd team', value=secondteam)
        await ctx.reply(embed=embed)
    
    # TODO cache the id to name mapping
    async def get_characters(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        characters = await client.get_starrail_characters(uid=account.starrail_uid)
        mapping = {}
        for character in characters.avatar_list:
            mapping[character.id] = character.name
        return mapping

    async def get_moc(self, account: HoyolabAccount, prevFlag):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_starrail_challenge(uid=account.starrail_uid, previous=prevFlag)
