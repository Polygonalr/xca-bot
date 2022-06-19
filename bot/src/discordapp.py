import nextcord
import json
import os
import asyncio
from io import BytesIO
import traceback
from nextcord.ext import commands
import genshin as gs
import sys
import datetime
import time
from configFile import token, owner_id, channel_whitelist
from enka import get_file_content_chrome, extract_enka_image

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, '../../cookies.json')) as f:
    data = json.load(f)

def restrict_channel(ctx):
    return isinstance(ctx.channel, nextcord.channel.DMChannel) or (len(channel_whitelist()) == 0 or ctx.channel.name in channel_whitelist())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=nextcord.Activity(name="the cookie jar", type=nextcord.ActivityType.listening))

# For debugging purposes and sticker ripping!
@bot.event
async def on_message(ctx):
    if isinstance(ctx.channel, nextcord.channel.DMChannel):
        if bot.user.mentioned_in(ctx):
            if (len(ctx.stickers) != 0):
                await ctx.reply("`" + ctx.stickers[0].url + "`")
            else:
                await ctx.reply("`" + ctx.content + "`")
    await bot.process_commands(ctx)

@bot.command(description="Get some help.")
async def help(ctx):
    embed = nextcord.Embed(title="PetBot's Help")
    for command in bot.walk_commands():
        description = command.description
        if not description or description is None or description == "":
            description = "No Description Provided."
        embed.add_field(name=f"`${command.name}{(' ' + command.signature) if command.signature is not None else ''}`", value=description, inline=False)
    await ctx.send(embed=embed)

@bot.command(description="Play ping pong with the bot.")
async def ping(ctx):
    await ctx.reply('Pong!')

@bot.command(description="Sends a reminder after specified time. Usage: `$remind what_to_remind HH:MM:SS`")
async def remind(ctx, reminder, time):
    remind_time = datetime.datetime.strptime(time, '%H:%M:%S')
    seconds_to_reminder = (remind_time - datetime.datetime(1970,1,1)).seconds
    embed = nextcord.Embed(
            description="Setting a reminder: " + reminder + ". Time set: " + str(seconds_to_reminder) + " seconds later.",
            colour=nextcord.Colour.gold(),
            )
    await ctx.reply(embed=embed)
    await asyncio.sleep(seconds_to_reminder)
    embed = nextcord.Embed(
            description="Reminder: " + reminder,
            colour=nextcord.Colour.brand_green(),
            )
    await ctx.reply(embed=embed)


@bot.command(description="Check logs for automatic daily Hoyolab check-in.")
async def checkinlogs(ctx):
    logs = open("../../../checkin-log.txt", "r")
    await ctx.reply("```" + logs.read() + "```")

@bot.command(description="[Owner-locked] Reloads cookies from cookies.json.")
async def reloadcookies(ctx):
    if ctx.author.id != owner_id():
        embed = nextcord.Embed(
                description="Error: only my master can use this command uwu",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return
    with open(os.path.join(__location__, 'cookies.json')) as f:
        data = json.load(f)
        embed = nextcord.Embed(
                description="Cookies reloaded!",
                colour=nextcord.Colour.brand_green(),
                )
        await ctx.reply(embed=embed)

@bot.command(description="Lists down every Hoyolab account in cookies.json.")
async def list(ctx):
    name, uid = [], []
    for acc in data:
        name.append(acc['name'])
        uid.append(acc['uid'])
    embed = nextcord.Embed(
            title="Displaying every account under my control",
            colour=nextcord.Colour.brand_green(),
            )
    embed.add_field(name='Name', value="\n".join(name))
    embed.add_field(name='uid', value="\n".join(map(lambda x: str(x), uid)))
    await ctx.reply(embed=embed)


@bot.command(description="Redeems a Genshin code for every account that has `cookie_token` set.")
async def redeem(ctx, code=None):
    '''if ctx.author.id != owner_id():
        embed = nextcord.Embed(
                description="Error: only my master can use this command uwu",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return'''
    if code == None:
        embed = nextcord.Embed(
                description="Error: please specify a code.\nUsage: $redeem <code>",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return
    embed = nextcord.Embed(
            description="Redemption in progress...",
            colour=nextcord.Colour.brand_green(),
            )
    await ctx.reply(embed=embed)
    logs = await redeem_code(code)
    if 'Invalid redemption code' in logs[0]['status']:
        embed = nextcord.Embed(
                description="Invalid code " + code + " provided!",
                colour=nextcord.Colour.brand_red(),
                )
    else:
        status_list = map(concat_status_string, logs)
        description = ""
        for status in status_list:
            description += status + "\n"
        description += "\n Redemption completed!"
        embed = nextcord.Embed(
                description=description,
                colour=nextcord.Colour.gold(),
                )
    await ctx.reply(embed=embed) 

@bot.command(description="Redeems a Genshin code for a specified username only.")
async def redeemfor(ctx, name=None, code=None):
    if name == None:
        embed = nextcord.Embed(
                description="Error: please specify who you want to redeem for.\nUsage: $redeemfor <name> <code>",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return
    elif code == None:
        embed = nextcord.Embed(
                description="Error: please specify a code.\nUsage: $redeemfor <name> <code>",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return

    embed = nextcord.Embed(
            description="Redemption in progress...",
            colour=nextcord.Colour.brand_green(),
            )
    await ctx.reply(embed=embed)
    logs = await redeem_code_for_user(name, code)
    embed = nextcord.Embed(
            description=logs,
            colour=nextcord.Colour.gold(),
            )
    await ctx.reply(embed=embed)

@bot.command(description="Lists down Spiral Abyss details.")
async def abyss(ctx, name=None, prev=None):
    if not restrict_channel(ctx):
        return
    prevFlag = False
    if name == None or name == "prev":
        user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
    else:
        user = next((acc for acc in data if acc['name'] == name), None)
    if name == "prev" or prev == "prev":
        prevFlag = True
    if user != None:
        spiral_abyss = await get_abyss(user, prevFlag)
        desc = "Total battles: {}\nTotal wins: {}\nMax floor: {}\nTotal stars: {}\n"\
            .format(spiral_abyss.total_battles, spiral_abyss.total_wins, spiral_abyss.max_floor, spiral_abyss.total_stars)

        floors = spiral_abyss.floors
        floor_12 = next((floor for floor in floors if floor.floor == 12), None)
        if prevFlag:
            embed = nextcord.Embed(
                    title="Previous cycle abyss stats for " + user['name'],
                    description=desc,
                    colour=nextcord.Colour.brand_green(),
                    )
        else:
            embed = nextcord.Embed(
                    title="Abyss stats for " + user['name'],
                    description=desc,
                    colour=nextcord.Colour.brand_green(),
                    )
        if floor_12 != None:
            embed.add_field(name='Showing stats for floor 12 only.', value='\u200b', inline=False)
            firsthalf = ""
            secondhalf = ""
            stars = ""
            for chamber in floor_12.chambers:
                battles = chamber.battles
                for chars in battles[0].characters:
                    firsthalf += chars.name + ' (lvl ' + str(chars.level) + ')' + '\n'
                firsthalf += "\n"
                for chars in battles[1].characters:
                    secondhalf += chars.name + ' (lvl ' + str(chars.level) + ')' + '\n'
                    stars += "\n"
                secondhalf += "\n"
                stars += str(chamber.stars) + " <:abyssstar:948380524462878760>\n"
            embed.add_field(name='1st half', value=firsthalf)
            embed.add_field(name='2nd half', value=secondhalf)
            embed.add_field(name='Stars', value=stars)
        else:
            not_found_msg = f"{user['name']} has not attempted floor 12 yet!"
            embed.add_field(name=not_found_msg, value='\u200b')
        await ctx.reply(embed=embed)

@bot.command(description="Don't shout. Alias for $notes.")
async def RE(ctx):
    if not restrict_channel(ctx):
        return
    await ctx.reply("There's no need to shout here!")
    await notes(ctx, None);

@bot.command(aliases=['re'], description="Get Real-time notes. Alias: `$re`")
async def notes(ctx, name=None):
    if not restrict_channel(ctx):
        return
    if name == None:
        user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
    else:
        user = next((acc for acc in data if acc['name'] == name), None)
    if user != None:
        try:
            notes = await get_notes(user)

            # resin section
            desc = "<:resin:927403591818420265>" + str(notes.current_resin) + "/160 "
            if int(notes.remaining_resin_recovery_time.total_seconds()) == 0:
                desc += "<:KleeDerp:861458796772589608>"
            else:
                maxout_time = datetime.datetime.now() + notes.remaining_resin_recovery_time
                desc += maxout_time.strftime("(Maxout - %I:%M %p)")

            desc += "\n"

            # realm currency section
            if int(notes.remaining_realm_currency_recovery_time.total_seconds()) == 0:
                desc += "<:realmcurrency:948030718087405598>Your teapot currency is probably full."
            else:
                desc += "<:realmcurrency:948030718087405598>" + str(notes.current_realm_currency) + "/" + str(notes.max_realm_currency) 

            # commission section
            #if notes['claimed_commission_reward'] == False:
                #desc += "\n\nCommissions not done! <:nonoseganyu:927411234226176040>"

            # parametric transformer
            desc += "\n<:parametric:971723428543479849> "
            if int(notes.remaining_transformer_recovery_time.total_seconds()) == 0:
                desc += "Ready to use!"
            else:
                epoch_time = int(time.time()) + int(notes.remaining_transformer_recovery_time.total_seconds())
                desc +="<t:" + str(epoch_time) + ":R>"

            desc += "\n\nExpeditions:\n"
            for idx, exp in enumerate(notes.expeditions):
                desc += str(idx + 1) + ". "
                if exp.status == 'Ongoing':
                    hours = int(int(exp.remaining_time.total_seconds()) / 60 / 60)
                    mins = int(int(exp.remaining_time.total_seconds()) / 60 - hours * 60)
                    expdone_time = datetime.datetime.now() + exp.remaining_time
                    desc += f"{str(hours)} hr {str(mins)} min remaining ({expdone_time.strftime('%I:%M %p')})"
                elif exp.status== 'Finished':
                    desc += ":white_check_mark: " + exp.status
                else:
                    desc += exp.status
                desc += "\n"
            embed = nextcord.Embed(
                    title="Notes for " + user['name'],
                    description=desc,
                    colour=nextcord.Colour.brand_green(),
                    )
            await ctx.reply(embed=embed)
        except gs.errors.DataNotPublic:
            embed = nextcord.Embed(
                    title="Notes for " + user['name'],
                    description="[Error: Account did not enable Real-Time Notes. Click here to do so.](https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html?#/ys/set)",
                    colour=nextcord.Colour.brand_red(),
                    )
            embed.set_image(url="https://media.discordapp.net/attachments/375466192397402124/927855237014884352/unknown.png")
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = nextcord.Embed(
                    title="Exception occured",
                    description=traceback.format_exc(),
                    colour=nextcord.Colour.brand_red(),
                    )
            await ctx.reply(embed=embed)

    else:
        embed = nextcord.Embed(
                description=f'Error: User not found: {name}',
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)

# Thanks shinshin.moe for the API!
@bot.command(description="Shows enka.shinshin link for a user, or extracts the enka character card for the specified character.")
async def enka(ctx, name=None, char=None):
    # Just restriction checking and arguments wrangling
    if not restrict_channel(ctx):
        return
    if name == None:
        user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
    else:
        user = next((acc for acc in data if acc['name'] == name), None)
        if user == None: # User must be specifying char name as first arg
            user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
            char = name

    if user != None:
        if char == None:
            embed = nextcord.Embed(
                    title="Enka.shinshin link for " + user['name'],
                    description=f"https://enka.shinshin.moe/u/{user['uid']}",
                    colour=nextcord.Colour.brand_green(),
                    )
            await ctx.reply(embed=embed)
        else:
            embed = nextcord.Embed(
                    title=f'Extracting Enka card for {user["name"]}\'s {char}...',
                    description="My server is slow, this command will take awhile. Please be patient!",
                    colour=nextcord.Colour.orange()
                    )
            await ctx.reply(embed=embed)
            img_bytes = extract_enka_image(user['uid'], char)
            if img_bytes == "priv":
                embed = nextcord.Embed(
                title="Error: Private Profile",
                description="Please enable the 'Show Character Details' option in your Character Showcase in-game to see the details.",
                colour=nextcord.Colour.brand_red(),
                )
                await ctx.reply(embed=embed)
            elif img_bytes == "no":
                embed = nextcord.Embed(
                description=f'Error: Char not found: {char}',
                colour=nextcord.Colour.brand_red(),
                )
                await ctx.reply(embed=embed)
            else:
                await ctx.send(file=nextcord.File(fp=BytesIO(img_bytes), filename='image.png'))
    else:
        embed = nextcord.Embed(
                description=f'Error: User not found: {name}',
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)

async def get_notes(user):
    client = gs.Client({"ltuid": user['ltuid'], "ltoken": user['ltoken']})
    notes = await client.get_genshin_notes(uid=user['uid'])
    # Force the API to actually give me the transformer recovery time
    # Still not sure whether this is the library's fault
    while notes.remaining_transformer_recovery_time is None:
        notes = await client.get_genshin_notes(uid=user['uid'])
    return notes

async def get_abyss(user, prevFlag):
    client = gs.Client({"ltuid": user['ltuid'], "ltoken": user['ltoken']})
    return await client.get_genshin_spiral_abyss(uid=user['uid'], previous=prevFlag)

async def redeem_code(code):
    redeemed_users = []
    for acc in data:
        if "cookie_token" in acc:
            redemptionAttempt = {
                "name": acc['name'],
                "status": "Not attempted",
            }
            client = gs.Client({"ltuid": acc['ltuid'], "ltoken": acc['ltoken'], "account_id": acc['ltuid'], "cookie_token": acc['cookie_token']})
            try:
                await client.redeem_code(code, uid=acc['uid'])
            except gs.GenshinException as e:
                redemptionAttempt['status'] = str(e)
            else:
                redemptionAttempt['status'] = "Redeemed!"
            redeemed_users.append(redemptionAttempt)
            if "Invalid redemption code" in redemptionAttempt['status']:
                return redeemed_users
            time.sleep(5)
    return redeemed_users

async def redeem_code_for_user(username, code):
    message = ""
    for acc in data:
        if username == acc['name']:
            client = gs.Client({"ltuid": acc['ltuid'], "ltoken": acc['ltoken'], "account_id": acc['ltuid'], "cookie_token": acc['cookie_token']})
            try:
                await client.redeem_code(code, uid=acc['uid'])
            except gs.GenshinException as e:
                return str(e)
            else:
                return "Redeemed!"
    return "Username not found!"

def concat_status_string(s):
    return s['name'] + ": " + s['status']


bot.run(token())
