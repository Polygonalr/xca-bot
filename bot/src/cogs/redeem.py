from enum import Enum
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context

from models import HoyolabAccount
from util import get_all_genshin_accounts_with_token, get_all_starrail_accounts_with_token, get_account_by_name

TIME_BETWEEN_REDEEMS = 2.5

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
        
    async def redeem_helper(self, ctx: Context, code: str, game_type: gs.Game):
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
            desc = "\n".join(status_list) + "\n\nRedemption completed!"
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
            description="Redemption in progres...",
            colour=Colour.brand_green(),
        )
        await ctx.reply(embed=embed)

        logs = await self.redeem_code_for_user(acc, code, game_type)

        embed = Embed(
            description=logs,
            colour=Colour.gold(),
        )
        await ctx.reply(embed=embed)

    # TODO Store the redeemed codes in the RedeemedGenshinCode model
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
        return redeemed_users

    # TODO Store the redeemed codes in the RedeemedStarRailCode model
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
                await client.redeem_code(code, uid=acc['uid'])
            except gs.GenshinException as e:
                redemption_attempt['status'] = str(e)
            else:
                redemption_attempt['status'] = "Redeemed!"
            redeemed_users.append(redemption_attempt)
            if "Invalid redemption code" in redemption_attempt['status']:
                return redeemed_users
            time.sleep(TIME_BETWEEN_REDEEMS)
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


