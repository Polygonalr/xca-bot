import datetime
import sys
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from models import HoyolabAccount
from util import get_genshin_acc_by_discord_id, \
    get_genshin_acc_by_name, \
    get_starrail_acc_by_discord_id, \
    get_starrail_acc_by_name

'''All emotes used in this cog.'''
RESIN = "<:resin:927403591818420265>"
KLEE_DERP = "<:KleeDerp:861458796772589608>"
REALM_CURRENCY = "<:realmcurrency:948030718087405598>"
PARAMETRIC = "<:parametric:971723428543479849>"
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"
TB_POWER = "<:trailblaze_power:1116269466095988746>"
BAILU_DANGO = "<:bailu_dango:1116271590942974002>"

'''Cog with command that shows Real-time notes for Genshin.'''
class Notes(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['re'], description="Get Real-time notes. Alias: `$re`")
    async def notes(self, ctx: Context, name: str=None):
        has_no_account = True
        
        genshin_account = get_genshin_acc_by_name(name) if name is not None else get_genshin_acc_by_discord_id(ctx.author.id)
        if genshin_account is not None:
            await self.genshin_notes(ctx, genshin_account)
            has_no_account = False    

        starrail_account = get_starrail_acc_by_name(name) if name is not None else get_starrail_acc_by_discord_id(ctx.author.id)
        if starrail_account is  not None:
            await self.starrail_notes(ctx, starrail_account)
            has_no_account = False

        if has_no_account:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin & Star Rail account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)

    async def genshin_notes(self, ctx: Context, genshin_account: HoyolabAccount):
        try:
            notes = await self.get_genshin_notes(genshin_account)

            # Resin
            desc = f"{RESIN} {notes.current_resin}/160"
            if int(notes.remaining_resin_recovery_time.total_seconds()) == 0:
                desc += KLEE_DERP
            else:
                maxout_time = datetime.datetime.now() + notes.remaining_resin_recovery_time
                desc += maxout_time.strftime(" (Maxout - %I:%M %p)")
            
            desc += "\n"

            # Realm Currency
            if int(notes.remaining_realm_currency_recovery_time.total_seconds()) == 0:
                desc += f"{REALM_CURRENCY} **Your teapot currency is probably full.**\n"
            else:
                desc += f"{REALM_CURRENCY} {notes.current_realm_currency}/{notes.max_realm_currency}\n"
            
            # Parametric Transformer
            if int(notes.remaining_transformer_recovery_time.total_seconds()) == 0:
                desc += f"{PARAMETRIC} **Ready to use!**"
            else:
                epoch_time = int(time.time()) + int(notes.remaining_transformer_recovery_time.total_seconds())
                desc += f"{PARAMETRIC} <t:{epoch_time}:R>"

            # Expeditions
            desc += "\n\n**Expeditions**\n"
            for idx, exp in enumerate(notes.expeditions):
                desc += f"{idx + 1}. "
                if exp.status == 'Ongoing':
                    hours = int(int(exp.remaining_time.total_seconds()) / 60 / 60)
                    mins = int(int(exp.remaining_time.total_seconds()) / 60 - hours * 60)
                    expdone_time = datetime.datetime.now() + exp.remaining_time
                    desc += f"{hours} hr {mins} min ({expdone_time.strftime('%I:%M %p')})"
                elif exp.status == 'Finished':
                    desc += ":white_check_mark: " + exp.status
                else:
                    desc += exp.status
                desc += "\n"
            embed = Embed(
                    title=f"{KIRARA_COOKIE} Genshin Notes for {genshin_account.name}",
                    description=desc,
                    colour=Colour.brand_green(),
                    )
            await ctx.reply(embed=embed)

        except gs.errors.DataNotPublic:
            embed = Embed(
                    title="Genshin Notes for " + genshin_account.name,
                    description="[Error: Account did not enable Real-Time Notes. Click here to do so.](https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html?#/ys/set)",
                    colour=Colour.brand_red(),
                    )
            embed.set_image(url="https://media.discordapp.net/attachments/375466192397402124/927855237014884352/unknown.png")
            await ctx.reply(embed=embed)

        except Exception as e:
            embed = Embed(
                    title="Exception occured",
                    description="This is likely due to on-going maintenance. If it is a genuine problem, please report it to the developer.",
                    colour=Colour.brand_red(),
                    )
            print(traceback.format_exc(), file=sys.stderr)
            await ctx.reply(embed=embed)

    async def starrail_notes(self, ctx: Context, starrail_account: HoyolabAccount):
        try:
            notes = await self.get_starrail_notes(starrail_account)

            # Trailblaze Power
            desc = f"{TB_POWER} {notes.current_stamina}/{notes.max_stamina}"
            if int(notes.stamina_recover_time.total_seconds()) == 0:
                desc += KLEE_DERP
            else:
                maxout_time = datetime.datetime.now() + notes.stamina_recover_time
                desc += maxout_time.strftime(" (Maxout - %I:%M %p)")

            # Assignments
            desc += "\n\n**Assignments**\n"
            for idx, exp in enumerate(notes.expeditions):
                desc += f"{idx + 1}. "
                if exp.status == 'Ongoing':
                    hours = int(int(exp.remaining_time.total_seconds()) / 60 / 60)
                    mins = int(int(exp.remaining_time.total_seconds()) / 60 - hours * 60)
                    expdone_time = datetime.datetime.now() + exp.remaining_time
                    desc += f"{hours} hr {mins} min ({expdone_time.strftime('%I:%M %p')})"
                elif exp.status == 'Finished':
                    desc += ":white_check_mark: " + exp.status
                else:
                    desc += exp.status
                desc += "\n"

            embed = Embed(
                    title=f"{BAILU_DANGO} Star Rail Notes for {starrail_account.name}",
                    description=desc,
                    colour=Colour.brand_green(),
                    )
            await ctx.reply(embed=embed)

        except gs.errors.DataNotPublic:
            embed = Embed(
                    title="Star Rail Notes for " + starrail_account.name,
                    description="[Error: Account did not enable Real-Time Notes. Click here to do so.](https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html?#/ys/set)",
                    colour=Colour.brand_red(),
                    )
            embed.set_image(url="https://media.discordapp.net/attachments/375466192397402124/927855237014884352/unknown.png")
            await ctx.reply(embed=embed)

        except Exception as e:
            embed = Embed(
                    title="Exception occured",
                    description="This is likely due to on-going maintenance. If it is a genuine problem, please report it to the developer.",
                    colour=Colour.brand_red(),
                    )
            print(traceback.format_exc(), file=sys.stderr)
            await ctx.reply(embed=embed)
    
    @commands.command(description="Don't shout. Alias for $notes.")
    async def RE(self, ctx):
        await ctx.reply("There's no need to shout here!")
        await self.notes(ctx, None)
        
    async def get_genshin_notes(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_genshin_notes(uid=account.genshin_uid)
    
    async def get_starrail_notes(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_starrail_notes(uid=account.starrail_uid)
