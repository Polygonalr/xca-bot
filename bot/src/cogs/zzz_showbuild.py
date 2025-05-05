import genshin as gs
from genshin.models import ZZZPartialAgent, ZZZFullAgent
import json
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from models import HoyolabAccount
from util import get_zzz_acc_by_discord_id, get_zzz_acc_by_name, hoyolab_client_init
from typing import List

'''Cog to show build of a character in ZZZ.'''
class ZZZShowBuild(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command(aliases=['shamez'], description="Shows the build of a character in ZZZ. Alias: `$shamez`",)
    async def zzzshowbuild(self, ctx: Context, name_arg: str=None, char_arg: str=None):
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
        
        zzz_account = get_zzz_acc_by_name(name) if name is not None else get_zzz_acc_by_discord_id(ctx.author.id)
        if zzz_account is None:
            embed = Embed(
                description="Error: User not found or does not have a Starrail account: {name}.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        char_list = await self.get_all_chars(zzz_account)
        agent = list(filter(lambda x: ''.join(filter(str.isalpha, x.name.lower())) == ''.join(filter(str.isalpha, char_name.lower())), char_list))
        if len(agent) == 0:
            embed = Embed(
                title="Error",
                description=f"Character {char_name} not found.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        char_info = await self.get_char_details(zzz_account, agent[0].id)

        embed_list = []

        engine_name = char_info.w_engine.name if char_info.w_engine is not None else "None"
        engine_lvl = char_info.w_engine.level if char_info.w_engine is not None else "None"
        engine_rank = char_info.w_engine.refinement if char_info.w_engine is not None else "None"

        main_embed = Embed(
            title=f"Showing build details for {zzz_account.name}'s {char_info.name} (M{char_info.rank})",
            description=f"W-Engine: {engine_name} (Lvl {engine_lvl} S{engine_rank})",
            colour=Colour.brand_green(),
        )
        curr_field_val = ""
        for property in char_info.properties:
            curr_field_val += f"{property.name}: {property.final}\n"
            if property.name == "CRIT DMG":
                main_embed.add_field(name="Stats", value=curr_field_val, inline=True)
                curr_field_val = ""
        main_embed.add_field(name="\u200b", value=curr_field_val, inline=True)

        disc_embed = Embed(
            title="Discs",
            colour=Colour.brand_green(),
        )
        for disc in char_info.discs:
            disc_stats = f"**{disc.main_properties[0].value} {disc.main_properties[0].name}**"
            for property in disc.properties:
                disc_stats += f"\n{property.value} {property.name}"
            disc_embed.add_field(name=f"{disc.name} ({disc.rarity}-rank Lvl {disc.level})", value=disc_stats, inline=True)
    

        embed_list.append(main_embed)
        embed_list.append(disc_embed)
        await ctx.reply(embeds=embed_list)
    
    async def get_all_chars(self, account: HoyolabAccount) -> List[ZZZPartialAgent]:
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        return await client.get_zzz_agents(uid=account.zzz_uid)

    async def get_char_details(self, account: HoyolabAccount, char_id: int) -> ZZZFullAgent:
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        return await client.get_zzz_agent_info(character_id=char_id, uid=account.zzz_uid)
