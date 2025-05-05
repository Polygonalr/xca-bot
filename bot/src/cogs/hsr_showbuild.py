import genshin as gs
from genshin.models import StarRailDetailCharacters
import json
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from models import HoyolabAccount
from util import get_starrail_acc_by_discord_id, get_starrail_acc_by_name, hoyolab_client_init

'''Cog to show build of a character in HSR.'''
class HSRShowBuild(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command(aliases=['shame'], description="Shows the build of a character in HSR. Alias: `$shame`",)
    async def hsrshowbuild(self, ctx: Context, name_arg: str=None, char_arg: str=None):
        if name_arg is None and char_arg is None:
            embed = Embed(
                title="Error",
                description="No.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return
        elif char_arg is None:
            char_name = name_arg
            name = None
        else:
            char_name = char_arg
            name = name_arg
        
        starrail_account = get_starrail_acc_by_name(name) if name is not None else get_starrail_acc_by_discord_id(ctx.author.id)
        if starrail_account is None:
            embed = Embed(
                description="Error: User not found or does not have a Starrail account: {name}.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        char_details = await self.get_char_details(starrail_account)
        char_info = list(filter(lambda x: ''.join(filter(str.isalpha, x.name.lower())) == ''.join(filter(str.isalpha, char_name.lower())), char_details.avatar_list))
        if len(char_info) == 0:
            embed = Embed(
                title="Error",
                description=f"Character {char_name} not found.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        embed_list = []

        light_cone_name = char_info[0].equip.name if char_info[0].equip is not None else "None"
        light_cone_lvl = char_info[0].equip.level if char_info[0].equip is not None else "None"
        light_cone_rank = char_info[0].equip.rank if char_info[0].equip is not None else "None"

        main_embed = Embed(
            title=f"Showing build details for {starrail_account.name}'s {char_info[0].name} (E{char_info[0].rank})",
            description=f"Light Cone: {light_cone_name} (Lvl {light_cone_lvl} S{light_cone_rank})",
            colour=Colour.brand_green(),
        )
        curr_field_val = ""
        for property in char_info[0].properties:
            curr_field_val += f"{property.info.name}: {property.final}\n"
            if property.info.name == "CRIT DMG":
                main_embed.add_field(name="Stats", value=curr_field_val, inline=True)
                curr_field_val = ""
        main_embed.add_field(name="\u200b", value=curr_field_val, inline=True)

        relic_embed = Embed(
            title="Relics",
            colour=Colour.brand_green(),
        )
        for relic in char_info[0].relics:
            relic_stats = f"**{relic.main_property.value} {relic.main_property.info.name}**"
            for property in relic.properties:
                relic_stats += f"\n{property.value} {property.info.name}"
            relic_embed.add_field(name=f"{relic.name} ({relic.rarity}* Lvl {relic.level})", value=relic_stats, inline=True)
        
        for relic in char_info[0].ornaments:
            relic_stats = f"{relic.main_property.value} {relic.main_property.info.name}"
            for property in relic.properties:
                relic_stats += f"\n{property.value} {property.info.name}"
            relic_embed.add_field(name=f"{relic.name} ({relic.rarity}* Lvl {relic.level})", value=relic_stats, inline=True)

        embed_list.append(main_embed)
        embed_list.append(relic_embed)
        await ctx.reply(embeds=embed_list)
    
    async def get_char_details(self, account: HoyolabAccount) -> StarRailDetailCharacters:
        client = hoyolab_client_init(account, gs.Game.STARRAIL)
        return await client.get_starrail_characters(uid=account.starrail_uid)
