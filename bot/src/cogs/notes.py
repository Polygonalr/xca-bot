import datetime
import sys
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from database import db_session
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
PRIMOGEM = "<:primogem:1122773414751510578>"
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"
TB_POWER = "<:trailblaze_power:1116269466095988746>"
BAILU_DANGO = "<:bailu_dango:1116271590942974002>"
KIRANYAN = "<:kiranyan1:1126353426880667688><:kiranyan2:1126353457570402364>" * 3 + "<:kiranyan3:1126353472065917028>"

CHECKIN_URL = "https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481"

'''Cog with command that shows Real-time notes for Genshin.'''
class Notes(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['re'], description="Get Real-time notes. Alias: `$re`")
    async def notes(self, ctx: Context, name: str=None):
        has_no_account = True
        output = []
        
        try:
            genshin_account = get_genshin_acc_by_name(name) if name is not None else get_genshin_acc_by_discord_id(ctx.author.id)
            if genshin_account is not None:
                has_no_account = False
                output.append(await self.genshin_notes(ctx, genshin_account))
        except gs.errors.DataNotPublic:
            embed = Embed(
                    title="Genshin Notes for " + genshin_account.name,
                    description="[Error: Account did not enable Real-Time Notes. Click here to do so.](https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html?#/ys/set)",
                    colour=Colour.brand_red(),
                    )
            embed.set_image(url="https://media.discordapp.net/attachments/375466192397402124/927855237014884352/unknown.png")
            await ctx.reply(embed=embed)
        except Exception as e:
            output.append({
                "title": "Exception occured while retrieving Genshin notes",
                "description": "This is likely due to on-going maintenance.\n" + \
                    "The exception has been logged down, so if it is a genuine problem, please report it to the developer.",
            })
            print(traceback.format_exc(), file=sys.stderr)
            await ctx.reply(embed=embed)

        try:
            starrail_account = get_starrail_acc_by_name(name) if name is not None else get_starrail_acc_by_discord_id(ctx.author.id)
            if starrail_account is not None:
                has_no_account = False
                output.append(await self.starrail_notes(ctx, starrail_account))
        except Exception as e:
            output.append({
                "title": "Exception occured while retrieving Star Rail notes",
                "description": "This is likely due to on-going maintenance.\n" + \
                    "The exception has been logged down, so if it is a genuine problem, please report it to the developer.",
            })
            print(traceback.format_exc(), file=sys.stderr)
            await ctx.reply(embed=embed)

        if has_no_account:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin & Star Rail account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return

        if len(output) > 1:
            for i in range(len(output) - 1):
                output[i]['description'] += f"\n{KIRANYAN}"
        
        embed = Embed(title=KIRANYAN, colour=Colour.brand_green())
        for note in output:
            embed.add_field(name=note["title"], value=note["description"], inline=False)
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
            
            # Daily check-in
            checkin_text = f":ballot_box_with_check:" if (await self.get_genshin_checkin(genshin_account)).signed_in \
                    else f":x: *[(Click here to check-in!)]({CHECKIN_URL})*"
            desc += f"\n{PRIMOGEM} Daily Check-in: {checkin_text}\n\n"

            # Expeditions
            desc += "**Expeditions**\n"
            expedition_counter = {}
            for exp in notes.expeditions:
                if exp.status == 'Ongoing':
                    expdone_time = (datetime.datetime.now() + exp.remaining_time).strftime("%I:%M %p")
                    expedition_counter[expdone_time] = expedition_counter[expdone_time] + 1 if expdone_time in expedition_counter else 1
                elif exp.status == 'Finished':
                    expedition_counter['now'] = expedition_counter['now'] + 1 if 'now' in expedition_counter else 1

            if 'now' in expedition_counter:
                desc += f"{expedition_counter['now']} expedition(s) ready to collect! :white_check_mark:\n"
            for expdone_time in sorted(expedition_counter.keys()):
                if expdone_time == "now":
                    continue
                desc += f"{expedition_counter[expdone_time]} ready at {expdone_time}\n"

            return {
                "title": f"{KIRARA_COOKIE} Genshin Notes for {genshin_account.name}",
                "description": desc,
            }
        except Exception as e:
            # pass back to the main function to handle
            raise e

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
            assignment_counter = {}
            for exp in notes.expeditions:
                if exp.status == 'Ongoing':
                    ts = int(exp.remaining_time.total_seconds())
                    expdone_time = (datetime.datetime.now() + datetime.timedelta(seconds=ts)).strftime('%I:%M %p')
                    assignment_counter[expdone_time] = assignment_counter[expdone_time] + 1 if expdone_time in assignment_counter else 1
                elif exp.status == 'Finished':
                    assignment_counter["now"] = assignment_counter["now"] + 1 if "now" in assignment_counter else 1
                
            if "now" in assignment_counter:
                desc += f"{assignment_counter['now']} assignment(s) ready to collect! :white_check_mark:\n"
            for expdone_time in sorted(assignment_counter.keys()):
                if expdone_time == "now":
                    continue
                desc += f"{assignment_counter[expdone_time]} ready at {expdone_time}\n"
            desc += "\n"

            return {
                "title": f"{BAILU_DANGO} Star Rail Notes for {starrail_account.name}",
                "description": desc,
            }
        except Exception as e:
            # pass back to the main function to handle
            raise e
    
    @commands.command(description="Don't shout. Alias for $notes.")
    async def RE(self, ctx):
        await ctx.reply("There's no need to shout here!")
        await self.notes(ctx, None)
        
    async def get_genshin_notes(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_genshin_notes(uid=account.genshin_uid)

    async def get_genshin_checkin(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_reward_info(game=gs.Game.GENSHIN)

    async def get_starrail_notes(self, account: HoyolabAccount):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        return await client.get_starrail_notes(uid=account.starrail_uid)
