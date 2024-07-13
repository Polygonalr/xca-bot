import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from util import get_genshin_acc_by_discord_id, get_genshin_acc_by_name, hoyolab_client_init

'''All emotes used in this cog'''
ABYSS_STAR = "<:abyssstar:948380524462878760>"

'''Cog which contains all commands for showing Spiral Abyss information.'''
class Abyss(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Shows details about the current Spiral Abyss cycle clear.")
    async def abyss(self, ctx: Context, name: str=None, prev: str=None):
        '''Initialisation and checks'''
        prevFlag = False
        if name in [None, "prev", "recap"]: # Retrieve data for the sender
            account = get_genshin_acc_by_discord_id(ctx.author.id)
        else:
            account = get_genshin_acc_by_name(name)
        if name == "prev" or prev == "prev":
            prevFlag = True
        if name == "recap":
            await self.abyssrecap(ctx)
            return

        if account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        '''Checks should be all ok by here, proceed with data retrieval'''
        spiral_abyss = await self.get_abyss(account, prevFlag)
        desc = "Total battles: {} | Total wins: {}\nMax floor: {} | Total stars: {}\n"\
            .format(spiral_abyss.total_battles, spiral_abyss.total_wins, spiral_abyss.max_floor, spiral_abyss.total_stars)
        floors = spiral_abyss.floors
        floor_12 = next((floor for floor in floors if floor.floor == 12), None)
        if prevFlag:
            embed = Embed(
                    title=f"Previous cycle abyss stats for {account.name}",
                    colour=Colour.brand_green(),
                    )
        else:
            embed = Embed(
                    title=f"Abyss stats for {account.name}",
                    colour=Colour.brand_green(),
                    )
            
        '''Format floor 12 clear details'''
        if floor_12 != None:
            embed.add_field(name='Showing stats for floor 12 only.', value='\u200b', inline=False)
            firsthalf = ""
            secondhalf = ""
            stars = ""
            for chamber in floor_12.chambers:
                battles = chamber.battles
                firsthalf += "\n".join(map(lambda chars: f"{chars.name} (lvl {chars.level})", battles[0].characters)) + "\n\n"
                secondhalf += "\n".join(map(lambda chars: f"{chars.name} (lvl {chars.level})", battles[1].characters)) + "\n\n"
                stars += f"{chamber.stars} {ABYSS_STAR}" + "\n" * max(len(battles[0].characters), len(battles[1].characters)) + "\n"
            embed.add_field(name='1st half', value=firsthalf)
            embed.add_field(name='2nd half', value=secondhalf)
            embed.add_field(name='Stars', value=stars)

            '''Calculate time taken between 9-1 and 12-3'''
            if len(floor_12.chambers) == 3:
                floor_9 = next((floor for floor in floors if floor.floor == 9), None)
                floor_10 = next((floor for floor in floors if floor.floor == 10), None)
                floor_11 = next((floor for floor in floors if floor.floor == 11), None)
                if floor_9.chambers[0].battles[0].timestamp < floor_10.chambers[0].battles[0].timestamp and \
                    floor_10.chambers[0].battles[0].timestamp < floor_11.chambers[0].battles[0].timestamp and \
                    floor_11.chambers[0].battles[0].timestamp < floor_12.chambers[0].battles[0].timestamp:
                    time_taken = floor_12.chambers[2].battles[1].timestamp - floor_9.chambers[0].battles[0].timestamp
                    desc += f"Time taken between 9-1 and 12-3: {time_taken}\n"
                else:
                    desc += f"{account.name} did not complete floors 9 to 12 in order. Time taken to clear spiral abyss cannot be estimated."
        else:
            not_found_msg = f"{account.name} has not attempted floor 12 yet!"
            embed.add_field(name=not_found_msg, value='\u200b')

        embed.description = desc
        await ctx.reply(embed=embed)

    @commands.command(description="Recaps characters used in the previous Spiral Abyss cycle clear.")
    async def abyssrecap(self, ctx: Context, name: str=None):
        floors = [9, 10, 11, 12]
        if name == None:
            account = get_genshin_acc_by_discord_id(ctx.author.id)
        else:
            account = get_genshin_acc_by_name(name)
        
        if account == None:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return
        
        spiral_abyss = await self.get_abyss(account, True)
        embed = Embed(
                title=f"Showing abyss recap for {account.name}",
                colour=Colour.brand_green(),
                )
        for floor_number in floors:
            curr = next((floor for floor in spiral_abyss.floors if floor.floor == floor_number), None)
            if curr == None:
                break
            embed.add_field(name=f"Characters used for floor {floor_number} chamber 1", value='\u200b', inline=False)
            first_chamber = curr.chambers[0]
            battles = first_chamber.battles
            firsthalf, secondhalf = "\n".join([c.name for c in battles[0].characters]), "\n".join([c.name for c in battles[1].characters])
            embed.add_field(name='1st half', value=firsthalf)
            embed.add_field(name='2nd half', value=secondhalf)
        await ctx.reply(embed=embed)
            

    
    async def get_abyss(self, account, prevFlag):
        client = hoyolab_client_init(account, gs.Game.GENSHIN)
        return await client.get_genshin_spiral_abyss(uid=account.genshin_uid, previous=prevFlag)
