import nextcord
import json
import os
import asyncio
from nextcord.ext import commands
import genshinstats as gs
import sys
import datetime
import time
from configFile import token, ownerId

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'cookies.json')) as f:
    data = json.load(f)

def restrict_channel(ctx):
    if isinstance(ctx.channel, nextcord.channel.DMChannel) or ctx.channel.name in ['coding-room', 'genshin-bot']:
        return True
    return False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=nextcord.Activity(name="the cookie jar", type=nextcord.ActivityType.listening))

@bot.command()
async def ping(ctx):
    await ctx.reply('Pong!')

@bot.command()
async def checkinlogs(ctx):
    logs = open("../checkin-log.txt", "r")
    await ctx.reply("```" + logs.read() + "```")

@bot.command()
async def redeem(ctx, arg=None):
    if ctx.author.id != ownerId():
        embed = nextcord.Embed(
                description="Error: only my master can use this command uwu",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return
    if arg == None:
        embed = nextcord.Embed(
                description="Error: please specify a code",
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)
        return
    embed = nextcord.Embed(
            description="Redemption in progress...",
            colour=nextcord.Colour.brand_green(),
            )
    await ctx.reply(embed=embed)
    logs = await redeem_code(arg)
    if logs[0]['status'] == 'Invalid redemption code':
        embed = nextcord.Embed(
                description="Invalid code " + arg + " provided!",
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

# TODO retrieve full info
@bot.command()
async def abyss(ctx, arg=None):
    if not restrict_channel(ctx):
        return
    if arg == None:
        user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
    else:
        user = next((acc for acc in data if acc['name'] == arg), None)
    if user != None:
        spiral_abyss = await get_abyss(user)
        stats = spiral_abyss['stats']
        desc = ""
        for field, value in stats.items():
            desc += f"{field}: {value}\n"

        floors = spiral_abyss['floors']
        floor_12 = next((floor for floor in floors if floor['floor'] == 12), None)
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
            for chamber in floor_12['chambers']:
                battles = chamber['battles']
                for chars in battles[0]['characters']:
                    firsthalf += chars['name'] + ' (lvl ' + str(chars['level']) + ')' + '\n'
                firsthalf += "\n"
                for chars in battles[1]['characters']:
                    secondhalf += chars['name'] + ' (lvl ' + str(chars['level']) + ')' + '\n'
                    stars += "\n"
                secondhalf += "\n"
                stars += str(chamber['stars']) + " stars\n"
            embed.add_field(name='1st half', value=firsthalf)
            embed.add_field(name='2nd half', value=secondhalf)
            embed.add_field(name='Stars', value=stars)
        else:
            not_found_msg = f"{user['name']} has not attempted floor 12 yet!"
            embed.add_field(name=not_found_msg, value='\u200b')
        await ctx.reply(embed=embed)

@bot.command()
async def RE(ctx):
    if not restrict_channel(ctx):
        return
    await ctx.reply("There's no need to shout here!")
    await notes(ctx, None);

@bot.command(aliases=['re'])
async def notes(ctx, arg=None):
    if not restrict_channel(ctx):
        return
    if arg == None:
        user = next((acc for acc in data if acc['discord_id'] == ctx.author.id), None)
    else:
        user = next((acc for acc in data if acc['name'] == arg), None)
    if user != None:
        try:
            notes = await get_notes(user)


            # resin section
            desc = "<:resin:927403591818420265>" + str(notes['resin']) + "/160 "
            if int(notes['until_resin_limit']) == 0:
                desc += "<:KleeDerp:861458796772589608>"
            else:
                maxout_time = datetime.datetime.now() + datetime.timedelta(seconds=int(notes['until_resin_limit']))
                desc += maxout_time.strftime("(Maxout - %I:%M %p)")

            # commission section
            # if notes['claimed_commission_reward'] == False:
                # desc += "\n\nCommissions not done! <:nonoseganyu:927411234226176040>"

            desc += "\n\nExpeditions:\n"
            for idx, exp in enumerate(notes['expeditions']):
                desc += str(idx + 1) + ". "
                if exp['status'] == 'Ongoing':
                    hours = int(int(exp['remaining_time']) / 60 / 60)
                    mins = int(int(exp['remaining_time']) / 60 - hours * 60)
                    expdone_time = datetime.datetime.now() + datetime.timedelta(seconds=int(exp['remaining_time']))
                    desc += f"{str(hours)} hr {str(mins)} min remaining ({expdone_time.strftime('%I:%M %p')})"
                elif exp['status'] == 'Finished':
                    desc += ":white_check_mark: " + exp['status']
                else:
                    desc += exp['status']
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
                    description=e,
                    colour=nextcord.Colour.brand_red(),
                    )
            await ctx.reply(embed=embed)

    else:
        embed = nextcord.Embed(
                description=f'Error: User not found: {arg}',
                colour=nextcord.Colour.brand_red(),
                )
        await ctx.reply(embed=embed)

async def get_notes(user):
    gs.set_cookie(ltuid=user['ltuid'], ltoken=user['ltoken'])
    return await asyncio.to_thread(gs.get_notes, user['uid'])

async def get_abyss(user):
    gs.set_cookie(ltuid=user['ltuid'], ltoken=user['ltoken'])
    return await asyncio.to_thread(gs.get_spiral_abyss, user['uid'])

async def redeem_code(code):
    redeemed_users = []
    for acc in data:
        if "cookie_token" in acc:
            redemptionAttempt = {
                "name": acc['name'],
                "status": "Not attempted",
            }
            gs.set_cookie(ltuid=acc['ltuid'], ltoken=acc['ltoken'], account_id=acc['ltuid'], cookie_token=acc['cookie_token'])
            try:
                await asyncio.to_thread(gs.redeem_code(code, uid=acc['uid']))
            except gs.CodeRedeemException as e:
                redemptionAttempt['status'] = str(e)
            except TypeError:
                # Not too sure why successful redemptions throws a TypeError but this is it.
                redemptionAttempt['status'] = "Redeemed!"
            else:
                redemptionAttempt['status'] = "Something went wrong that is not caught."
            redeemed_users.append(redemptionAttempt)
            if redemptionAttempt['status'] == "Invalid redemption code":
                return redeemed_users
            time.sleep(5)
    return redeemed_users

def concat_status_string(s):
    return s['name'] + ": " + s['status']


bot.run(token())
