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
    if len(logs) == 0:
        embed = nextcord.Embed(
                description="Invalid code " + arg + " provided!",
                colour=nextcord.Colour.brand_red(),
                )
    else:
        embed = nextcord.Embed(
                description="Tried to redeem for " + ", ".join(logs),
                colour=nextcord.Colour.brand_orange(),
                )
    await ctx.reply(embed=embed) 

@bot.command()
async def abyss(ctx, arg=None):
    if not ctx.channel.name in ['coding-room', 'genshin-bot']:
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
        embed = nextcord.Embed(
                title="Abyss stats for " + user['name'],
                description=desc,
                colour=nextcord.Colour.brand_green(),
                )
        await ctx.reply(embed=embed)

@bot.command(aliases=['re'])
async def notes(ctx, arg=None):
    if not ctx.channel.name in ['coding-room', 'genshin-bot']:
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

# TODO retrieve full info
async def get_abyss(user):
    gs.set_cookie(ltuid=user['ltuid'], ltoken=user['ltoken'])
    return await asyncio.to_thread(gs.get_spiral_abyss, user['uid'])

async def redeem_code(code):
    redeemed_users = []
    for acc in data:
        if "cookie_token" in acc:
            gs.set_cookie(ltuid=acc['ltuid'], ltoken=acc['ltoken'], account_id=acc['ltuid'], cookie_token=acc['cookie_token'])
            # TODO Set different cases for different exceptions
            try:
                await asyncio.to_thread(gs.redeem_code(code, uid=acc['uid']))
            except:
                return []
            redeemed_users.append(acc['name'])
            time.sleep(5)
    return redeemed_users

bot.run(token())
