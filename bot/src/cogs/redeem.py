from enum import Enum
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context

from models import HoyolabAccount
from util import get_all_genshin_accounts_with_token, \
    get_all_starrail_accounts_with_token, \
    get_account_by_name, \
    add_genshin_code as add_gs, \
    add_starrail_code as add_sr, \
    check_genshin_redeemed_code as check_gs, \
    check_starrail_redeemed_code as check_sr, \
    get_recent_genshin_codes as get_recent_gs, \
    get_recent_starrail_codes as get_recent_sr

TIME_BETWEEN_REDEEMS = 2.5
GENSHIN_REDEEM_LINK = "https://genshin.hoyoverse.com/en/gift?code="
STARRAIL_REDEEM_LINK = "https://hsr.hoyoverse.com/gift"

'''Cog which has commands to redeem codes for all accounts with cookie_token.'''
class Redeem(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Redeem code for all genshin accounts with cookie_token.")
    async def redeem(self, ctx: Context, code: str=None):
        if code == None:
            embed = Embed(
                description="Error: please specify a code.\nUsage: $redeem <code>",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        await self.redeem_helper(ctx, code, gs.Game.GENSHIN)

    @commands.command(description="Redeem code for all Star Rail accounts.")
    async def sredeem(self, ctx: Context, code: str=None):
        if code == None:
            embed = Embed(
                description="Error: please specify a code.\nUsage: $redeem <code>",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        await self.redeem_helper(ctx, code, gs.Game.STARRAIL)

    @commands.command(description="Redeem a Genshin code for a specific account.")
    async def redeemfor(self, ctx: Context, name: str=None, code: str=None):
        await self.redeem_for_helper(ctx, name, code, gs.Game.GENSHIN)
    
    @commands.command(description="Redeem a Star Rail code for a specific account.")
    async def sredeemfor(self, ctx: Context, name: str=None, code: str=None):
        self.redeem_for_helper(ctx, name, code, gs.Game.STARRAIL)
    
    @commands.command(description="Lists down all the code that was redeemed last 24 hours.")
    async def redeemlist(self, ctx: Context):
        recent_gs = list(map(lambda x: f'`{x.code}` [(LINK)]({GENSHIN_REDEEM_LINK + x.code})', get_recent_gs()))
        recent_sr = list(map(lambda x: f'`{x.code}` [(LINK)]({STARRAIL_REDEEM_LINK})', get_recent_sr()))
        desc = "**Genshin codes redeemed in the last 24 hours**\n\n" \
            + "\n".join(recent_gs if len(recent_gs) != 0 else ["*No codes redeemed recently!*"]) \
            + "\n\n**Star Rail codes redeemed in the last 24 hours**\n\n" \
            + "\n".join(recent_sr if len(recent_sr) != 0 else ["*No codes redeemed recently!*"])
        embed = Embed(
            description=desc,
            colour=Colour.gold(),
        )
        await ctx.reply(embed=embed)
        
    async def redeem_helper(self, ctx: Context, code: str, game_type: gs.Game):
        # ON THE ASSUMPTION THAT GENSHIN CODES WILL NOT BE THE SAME AS STAR RAIL CODES
        if check_gs(code) or check_sr(code):
            embed = Embed(
                description="Error: code has already been redeemed.",
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        embed = Embed(
            description=f"[{game_type}] Redemption in progress...",
            colour=Colour.brand_green(),
        )
        await ctx.reply(embed=embed)

        if game_type == gs.Game.GENSHIN:
            logs = await self.redeem_genshin_code(code)
        else:
            logs = await self.redeem_starrail_code(code)
        
        if len(logs) == 0:
            embed = Embed(
                description="No accounts to redeem code for!",
                colour=Colour.brand_red(),
            )
        elif 'Invalid redemption code' in logs[0]['status']:
            embed = Embed(
                description="Invalid code " + code + " provided!",
                colour=Colour.brand_red(),
            )
        else:
            status_list = map(lambda s: f"{s['name']}: {s['status']}", logs)
            desc = "\n".join(status_list) + "\n\nRedemption completed! [Click here for direct link.](" \
                    + (GENSHIN_REDEEM_LINK + code if game_type == gs.Game.GENSHIN else STARRAIL_REDEEM_LINK) + ")"

            desc = f"`{code}`\n\n" + desc
            embed = Embed(
                description=desc,
                colour=Colour.gold(),
            )

        await ctx.reply(embed=embed)
    
    async def redeem_for_helper(self, ctx: Context, name: str, code: str, game_type: gs.Game):
        if name == None:
            embed = Embed(
                description="Error: please specify a name.\nUsage: $redeemfor <name> <code>",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        elif code == None:
            embed = Embed(
                description="Error: please specify a code.\nUsage: $redeemfor <name> <code>",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return

        acc = get_account_by_name(name)
        if acc == None:
            embed = Embed(
                description="Error: account not found.",
                colour=Colour.brand_red()
            )
        if acc.cookie_token == None:
            embed = Embed(
                description="Error: this account does not have a cookie token.",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        if acc.genshin_uid == None and game_type == gs.Game.GENSHIN:
            embed = Embed(
                description="Error: this account does not have a Genshin uid.",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        if acc.starrail_uid == None and game_type == gs.Game.STARRAIL:
            embed = Embed(
                description="Error: this account does not have a Star Rail uid.",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return

        embed = Embed(
            description="Redemption in progress...",
            colour=Colour.brand_green(),
        )
        await ctx.reply(embed=embed)

        logs = await self.redeem_code_for_user(acc, code, game_type)

        embed = Embed(
            description=logs,
            colour=Colour.gold(),
        )
        await ctx.reply(embed=embed)

    async def redeem_genshin_code(self, code: str):
        redeemed_users = []
        for acc in get_all_genshin_accounts_with_token():
            redemption_attempt = {
                "name": acc.name,
                "status": "Not attempted",
            }
            client = gs.Client({
                "ltuid": acc.ltuid,
                "ltoken": acc.ltoken,
                "account_id": acc.ltuid,
                "cookie_token": acc.cookie_token,
            }, game=gs.Game.GENSHIN)
            try:
                await client.redeem_code(code, uid=acc.genshin_uid)
            except gs.GenshinException as e:
                redemption_attempt['status'] = str(e)
            else:
                redemption_attempt['status'] = "Redeemed!"
            redeemed_users.append(redemption_attempt)
            if "Invalid redemption code" in redemption_attempt['status']:
                return redeemed_users
            time.sleep(TIME_BETWEEN_REDEEMS)
        add_gs(code)
        return redeemed_users

    async def redeem_starrail_code(self, code: str):
        redeemed_users = []
        for acc in get_all_starrail_accounts_with_token():
            redemption_attempt = {
                "name": acc.name,
                "status": "Not attempted",
            }
            client = gs.Client({
                "ltuid": acc.ltuid,
                "ltoken": acc.ltoken,
                "account_id": acc.ltuid,
                "cookie_token": acc.cookie_token,
            }, game=gs.Game.STARRAIL)
            try:
                await client.redeem_code(code, uid=acc.starrail_uid)
            except gs.GenshinException as e:
                redemption_attempt['status'] = str(e)
            else:
                redemption_attempt['status'] = "Redeemed!"
            redeemed_users.append(redemption_attempt)
            if "Invalid redemption code" in redemption_attempt['status']:
                return redeemed_users
            time.sleep(TIME_BETWEEN_REDEEMS)
        add_sr(code)
        return redeemed_users

    async def redeem_code_for_user(self, acc: HoyolabAccount, code: str, game_type: gs.Game):
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
            "account_id": acc.ltuid,
            "cookie_token": acc.cookie_token,
        }, game=game_type)
        try:
            if game_type == gs.Game.GENSHIN:
                await client.redeem_code(code, uid=acc.genshin_uid)
            elif game_type == gs.Game.STARRAIL:
                await client.redeem_code(code, uid=acc.starrail_uid)
        except gs.GenshinException as e:
            return str(e)
        else:
            return "Redeemed!"


