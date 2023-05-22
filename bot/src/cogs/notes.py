import datetime
import time
import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from util import get_accounts_by_discord_id, get_accounts_by_name

'''All emotes used in this cog.'''
RESIN = "<:resin:927403591818420265>"
KLEE_DERP = "<:KleeDerp:861458796772589608>"
REALM_CURRENCY = "<:realmcurrency:948030718087405598>"
PARAMETRIC = "<:parametric:971723428543479849>"
KIRARA_COOKIE = "<:KiraraCookie:1110172718520873040>"

class Notes(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['re'], description="Get Real-time notes. Alias: `$re`")
    async def notes(self, ctx: Context, name: str=None):
        if name == None: # Retrieve data for the sender
            accounts = get_accounts_by_discord_id(ctx.author.id)
        else:
            accounts = get_accounts_by_name(name)
        accounts = list(filter(lambda acc: acc.genshin_uid is not None, accounts))

        if len(accounts) == 0:
            embed = Embed(
                description=f'Error: User not found or does not have a Genshin account: {name}',
                colour=Colour.brand_red(),
            )
            await ctx.reply(embed=embed)
            return
        
        # Assume only one account for now, will need to change when Star Rail adds stamina tracking as well.
        account = accounts[0]

        try:
            notes = await self.get_notes(account)

            # Resin
            desc = f"{RESIN} {notes.current_resin}/160"
            if int(notes.remaining_resin_recovery_time.total_seconds()) == 0:
                desc += KLEE_DERP
            else:
                maxout_time = datetime.datetime.now() + notes.remaining_resin_recovery_time
                desc += maxout_time.strftime(" (Maxout - %I:%M %p)")
            
            desc += "\n"

            # Real Currency
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
                elif exp.status== 'Finished':
                    desc += ":white_check_mark: " + exp.status
                else:
                    desc += exp.status
                desc += "\n"
            embed = Embed(
                    title=f"{KIRARA_COOKIE} Notes for {account.name}",
                    description=desc,
                    colour=Colour.brand_green(),
                    )
            await ctx.reply(embed=embed)

        except gs.errors.DataNotPublic:
            embed = Embed(
                    title="Notes for " + account.name,
                    description="[Error: Account did not enable Real-Time Notes. Click here to do so.](https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html?#/ys/set)",
                    colour=Colour.brand_red(),
                    )
            embed.set_image(url="https://media.discordapp.net/attachments/375466192397402124/927855237014884352/unknown.png")
            await ctx.reply(embed=embed)

        except Exception as e:
            embed = Embed(
                    title="Exception occured",
                    description=traceback.format_exc(),
                    colour=Colour.brand_red(),
                    )
            await ctx.reply(embed=embed)
        
    async def get_notes(self, account):
        client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})
        notes = await client.get_genshin_notes(uid=account.genshin_uid)
        return notes