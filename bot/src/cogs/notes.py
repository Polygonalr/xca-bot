import genshin as gs
from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
import traceback
from util import get_accounts_by_discord_id, get_accounts_by_name

"""All emotes used in this cog."""
RESIN = "<:resin:927403591818420265>"
KLEE_DERP = "<:KleeDerp:861458796772589608>"
REALM_CURRENCY = "<:realmcurrency:948030718087405598>"
PARAMETRIC = "<:parametric:971723428543479849>"

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
            desc = f"{RESIN} {notes.current_resin}/160"
            # TODO continue porting

        except gs.errors.DataNotPublic:
            embed = Embed(
                    title="Notes for " + account['name'],
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