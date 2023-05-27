from nextcord import Embed, Colour
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Context
from sqlalchemy.exc import IntegrityError
from models import DiscordUser, HoyolabAccount
from database import db_session
from dotenv import dotenv_values
from util import get_account_by_ltuid

config = dotenv_values(".env")

def is_owner(ctx: Context) -> bool:
    return ctx.author.id == int(config["OWNER_ID"])

'''Cog for all admin commands.'''
class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db_session = db_session
    
    @commands.command(description="Register the current discord user.")
    @commands.check(is_owner)
    async def register(self, ctx: Context, id: int=None):
        id_to_add = ctx.author.id
        if id != None:
            id_to_add = id

        try:
            self.db_session.add(DiscordUser(id_to_add))
            self.db_session.commit()
            await ctx.reply("Registered!")
        except  IntegrityError:
            await ctx.reply("Already registered!")

    @commands.command(description="Add a Hoyolab account.")
    @commands.check(is_owner)
    async def add_hoyolab_acc(self, ctx: Context, name: str=None, ltuid: int=None, ltoken: str=None, discord_user_id: str=None):
        if ltuid == None or ltoken == None or name == None or discord_user_id == None:
            await ctx.reply("Invalid arguments. Usage: $add_hoyolab_acc <name> <ltuid> <ltoken> <discord_user_id>")
            return

        discord_user_id = int("".join(list(filter(lambda x: x.isdigit(), discord_user_id))))

        try:
            self.db_session.add(HoyolabAccount(name, ltuid, ltoken, None, discord_user_id))
            self.db_session.commit()
            await ctx.reply("Added!")
        except  IntegrityError:
            await ctx.reply("Already added!")

    @commands.command(description="Add Genshin uid to Hoyolab account.")
    @commands.check(is_owner)
    async def add_genshin_uid(self, ctx: Context, name: str=None, uid: int=None):
        if name == None or uid == None:
            await ctx.reply("Invalid arguments. Usage: $add_genshin_uid <name> <uid>")
            return
        
        query = self.db_session.query(HoyolabAccount).filter(HoyolabAccount.name == name)
        if query.count() == 0:
            await ctx.reply("Account not found!")
            return

        try:
            account = query.first()
            account.genshin_uid = uid
            self.db_session.commit()
            await ctx.reply("Added!")
        except IntegrityError:
            await ctx.reply("Already added!")

    '''Copy and pasted code from above, should probably try to DRY'''
    @commands.command(description="Add Star Rail uid to Hoyolab account.")
    @commands.check(is_owner)
    async def add_starrail_uid(self, ctx: Context, name: str=None, uid: int=None):
        if name == None or uid == None:
            await ctx.reply("Invalid arguments. Usage: $add_starrail_uid <name> <uid>")
            return
        
        query = self.db_session.query(HoyolabAccount).filter(HoyolabAccount.name == name)
        if query.count() == 0:
            await ctx.reply("Account not found!")
            return

        try:
            account = query.first()
            account.starrail_uid = uid
            self.db_session.commit()
            await ctx.reply("Added!")
        except IntegrityError:
            await ctx.reply("Already added!")

    @commands.command(description="Update Hoyolab cookie_token for automated code redemption.")
    async def updatetoken(self, ctx: Context, cookie: str=None):
        COOKIE_UPDATE_INSTRUCTIONS = "1. [Click here to go to the code redemption page](https://hsr.hoyoverse.com/gift) and make sure you are logged in.\n" \
                    + "2. Open the developer console (CTRL+SHIFT+J on Chrome, CTRL+SHIFT+K on Firefox).\n" \
                    + "3. Copy and paste the following code into the console and press enter: `document.cookie`\n" \
                    + "4. Copy the output and paste it into the command.\n"

        if cookie == None:
            embed = Embed(
                description="Invalid arguments. Usage: `$update_token <cookie>`. To get your cookie:\n" + COOKIE_UPDATE_INSTRUCTIONS,
                colour=Colour.red()
            )
            await ctx.reply(embed=embed)
            return
        
        cookie = cookie.replace('"' , '').split("; ")
        ltuid = [x for x in cookie if x.startswith("account_id=")][0].split("=")[1]
        token = [x for x in cookie if x.startswith("cookie_token=")][0].split("=")[1]
        if ltuid == None or token == None:
            embed = Embed(
                description="Cookie format provided is invalid!\n" + COOKIE_UPDATE_INSTRUCTIONS,
                colour=Colour.red()
            )
            await ctx.reply(embed=embed)
            return

        account_to_update = get_account_by_ltuid(ltuid)
        if account_to_update == None:
            embed = Embed(
                description="Account with the associated cookie cannot be found!",
                colour=Colour.red()
            )
            await ctx.reply(embed=embed)
            return

        account_to_update.cookie_token = token
        self.db_session.commit()
        embed = Embed(
            description=f"<@{ctx.author.id}> Updated cookie token for {account_to_update.name}!",
            colour=Colour.green()
        )
        await ctx.reply(embed=embed)
        await ctx.message.delete()

        
