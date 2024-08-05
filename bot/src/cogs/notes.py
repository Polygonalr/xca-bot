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
    get_starrail_acc_by_name, \
    get_zzz_acc_by_discord_id, \
    get_zzz_acc_by_name, \
    hoyolab_client_init

'''All emotes used in this cog.'''
RESIN = "<:resin:927403591818420265>"
KLEE_DERP = "<:KleeDerp:861458796772589608>"
REALM_CURRENCY = "<:realmcurrency:948030718087405598>"
PARAMETRIC = "<:parametric:971723428543479849>"
PRIMOGEM = "<:primogem:1122773414751510578>"
COMMS = "<:comms:1167786484296843324>"
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"
TB_POWER = "<:trailblaze_power:1116269466095988746>"
DAILY_TRAINING = "<:dailytraining:1170268830422020177>"
KURUKURU = "<a:kurukuru:1166577731429998663>"
KIRANYAN = "<:kiranyan1:1126353426880667688><:kiranyan2:1126353457570402364>" * 3 + "<:kiranyan3:1126353472065917028>"
BANGBOO = "<:bangboo:1259442260010078250>"
BATTERY_CHARGE = "<:batterycharge:1259443153509941280>"
DAILY_ENGAGEMENT = "<:dailyengagement:1259442854950993961>"

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
        
        try:
            zzz_account = get_zzz_acc_by_name(name) if name is not None else get_zzz_acc_by_discord_id(ctx.author.id)
            if zzz_account is not None:
                has_no_account = False
                output.append(await self.zzz_notes(ctx,zzz_account))
        except Exception as e:
            output.append({
                "title": "Exception occured while retrieving ZZZ notes",
                "description": "This is likely due to on-going maintenance.\n" + \
                    "The exception has been logged down, so if it is a genuine problem, please report it to the developer.",
            })
            print(traceback.format_exc(), file=sys.stderr)

        if has_no_account:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin, Star Rail or ZZZ account: {name}',
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
            desc = f"{RESIN} {notes.current_resin}/{notes.max_resin}"
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
            
            # Daily check-in, retired for now since there's no more captcha
            # checkin_text = f":ballot_box_with_check:" if (await self.get_genshin_checkin(genshin_account)).signed_in \
            #         else f":x: *[(Click here to check-in!)]({CHECKIN_URL})*"
            # desc += f"\n{PRIMOGEM} Daily Check-in: {checkin_text}\n\n"

            dt = notes.daily_task 
            desc += f"\n{COMMS} {dt.completed_tasks}/{dt.max_tasks} done\n"
            if not dt.claimed_commission_reward:
                desc += "**Commission reward not claimed!** <:nonoseganyu:927411234226176040>\n"
            desc += "\n"

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

            # Daily Training
            desc += f"\n{DAILY_TRAINING} {notes.current_train_score}/{notes.max_train_score}"

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

            return {
                "title": f"{KURUKURU} Star Rail Notes for {starrail_account.name}",
                "description": desc,
            }
        except Exception as e:
            # pass back to the main function to handle
            raise e
    
    async def zzz_notes(self, ctx: Context, zzz_account: HoyolabAccount):
        try:
            notes = await self.get_zzz_notes(zzz_account)

            # Battery Charge
            desc = f"{BATTERY_CHARGE} {notes.battery_charge.current}/{notes.battery_charge.max}"
            if notes.battery_charge.seconds_till_full == 0:
                desc += KLEE_DERP
            else:
                maxout_time = datetime.datetime.now() + datetime.timedelta(seconds=notes.battery_charge.seconds_till_full)
                desc += maxout_time.strftime(" (Maxout - %I:%M %p)")

            # Daily Engagement
            desc += f"\n{DAILY_ENGAGEMENT} {notes.engagement.current}/{notes.engagement.max}"

            # Scratch Card
            if not notes.scratch_card_completed:
                desc += "\nScratch card not completed! :dog:"

            return {
                "title": f"{BANGBOO} ZZZ Notes for {zzz_account.name}",
                "description": desc
            }
        except Exception as e:
            raise e

    
    @commands.command(description="Don't shout. Alias for $notes.")
    async def RE(self, ctx):
        await ctx.reply(f"There's no need to shout here! {KURUKURU}")
        await self.notes(ctx, None)
        
    async def get_genshin_notes(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.GENSHIN)
        return await client.get_genshin_notes(uid=account.genshin_uid)

    async def get_genshin_checkin(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.GENSHIN)
        return await client.get_reward_info(game=gs.Game.GENSHIN)

    async def get_starrail_notes(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.STARRAIL)
        return await client.get_starrail_notes(uid=account.starrail_uid)

    async def get_zzz_notes(self, account: HoyolabAccount):
        client = hoyolab_client_init(account, gs.Game.ZZZ)
        return await client.get_zzz_notes(uid=account.zzz_uid)
