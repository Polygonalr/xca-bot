from enum import Enum
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from util import get_all_genshin_accounts_with_token, get_all_starrail_accounts_with_token

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
        await self.redeem_code_helper(ctx, code, gs.Game.GENSHIN)

    @commands.command(description="Redeem code for all Star Rail accounts.")
    async def sredeem(self, ctx: Context, code: str=None):
        if code == None:
            embed = Embed(
                description="Error: please specify a code.\nUsage: $redeem <code>",
                colour=Colour.brand_red()
            )
            await ctx.reply(embed=embed)
            return
        await self.redeem_code_helper(ctx, code, gs.Game.STARRAIL)
        
    async def redeem_code_helper(self, ctx: Context, code: str, game_type: gs.Game):
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
