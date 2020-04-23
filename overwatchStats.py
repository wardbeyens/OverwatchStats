import asyncio
from discord.ext import commands, tasks
import discord
import json
import aiohttp
import datetime
import os

TOKEN = open('token.txt').read()  # Get at discordapp.com/developers/applications/me
client = discord.Client()
prefix = '.'
bot = commands.Bot(command_prefix=prefix)
# -----------------------------------------------------------------------------------------------------------------------
@tasks.loop(hours=1)
async def changePull(*updateMessage):
    def updateJson(data, profilename):
        with open('profiles/' + profilename, 'w') as json_file:
            json.dump(data, json_file)

    def oldJson(profilename):
        with open('profiles/' + profilename) as json_file:
            data = json.load(json_file)
            return data

    async def getJson(profilename):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://ow-api.com/v1/stats/pc/eu/" + profilename + "/complete") as r:
                if r.status == 200:
                    data = await r.json()
        return data

    def constructMessageDif(avalibleRoles):
        def getSignDiff(new, old):
            diff = new - old
            if old is None:
                old = 0
            if new is None:
                new = 0
            if diff > 0:
                sign = '+' + str(diff)
            else:
                sign = str(diff)
            return sign

        def addField(new,old):
            diff = getSignDiff(new, old)
            embed.add_field(name=avalibleRoles[avalibleRoles.index(role)].capitalize() + " previous",
                            value='```' + str(old) + " SR```", inline=True)
            embed.add_field(name='Difference', value='```diff\n' + diff + '```', inline=True)
            embed.add_field(name=avalibleRoles[avalibleRoles.index(role)].capitalize() + " current",
                            value='```' + str(new) + " SR```", inline=True)
        embed = discord.Embed(title=currentData['name'].capitalize(), colour=discord.Colour(0xfa9c1d),
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name='Full profile', icon_url=currentData['ratingIcon'])
        embed.set_thumbnail(url=currentData['icon'])
        embed.set_footer(text="Made by Vic ♥ | ow-api.com")
        for role in avalibleRoles:
            if role == 'tank':
                addField(tankNew,tankOld)
            if role == 'damage':
                addField(damageNew, damageOld)
            if role == 'support':
                addField(supportNew, supportOld)
        return embed

    players = ['wabyte-2990', 'raifiss-2515', 'Victonator-2131', 'Ardipithecus-2952',
               'AikaNoodle-2123','Che-21446']
    for name in players:
        if not os.path.exists('profiles/'):
            print('Directory not found, creating new directory')
            os.mkdir('profiles')
        if not os.path.exists('profiles/' + name):
            print("Downloading new profile", name)
            updateJson(await getJson(name), name)

        avalibleRolesOld = []
        avalibleRolesNew = []
        oldData = oldJson(name)
        currentData = await getJson(name)
        tankNew = None;
        tankOld = None;
        damageNew = None;
        damageOld = None;
        supportNew = None;
        supportOld = None

        if not currentData['ratings'] == None:
            for field in range(len(currentData['ratings'])):
                avalibleRolesNew.append(currentData['ratings'][field]['role'].lower())
        if not oldData['ratings'] == None:
            for field in range(len(oldData['ratings'])):
                avalibleRolesOld.append(oldData['ratings'][field]['role'].lower())

        for role in avalibleRolesNew:
            if role == 'tank':
                tankNew = currentData['ratings'][avalibleRolesNew.index(role)]['level']
            if role == 'damage':
                damageNew = currentData['ratings'][avalibleRolesNew.index(role)]['level']
            if role == 'support':
                supportNew = currentData['ratings'][avalibleRolesNew.index(role)]['level']

        for role in avalibleRolesOld:
            if role == 'tank':
                tankOld = oldData['ratings'][avalibleRolesOld.index(role)]['level']
            if role == 'damage':
                damageOld = oldData['ratings'][avalibleRolesOld.index(role)]['level']
            if role == 'support':
                supportOld = oldData['ratings'][avalibleRolesOld.index(role)]['level']

        if tankOld != tankNew or damageOld != damageNew or supportOld != supportNew:
            updateJson(currentData, name)
            if len(avalibleRolesNew)>=len(avalibleRolesOld):
                embed = constructMessageDif(avalibleRolesNew)
            else:
                embed = constructMessageDif(avalibleRolesOld)
            channel = bot.get_channel(id=701798038267494491)
            await channel.send(embed=embed)
            print(name, "Updating...")
        else:
            print(name, "Not updating...")
        if updateMessage:
            await updateMessage[0].edit(content="Updating ranks ..." + ' ...' * players.index(name))
    if updateMessage:
        await updateMessage[0].edit(content="Ranks updated!")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    activity = discord.Activity(name='data 👀', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command does not exist. Try "+prefix+"``help`` for a list of commands")
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("The command seems to be incomplete, try " + prefix + '``help (command)``')

@bot.command(name='profile')
async def profile(ctx, profilename, *role):
    nameToUser = {"ward":"wabyte-2990", "raif":"raifiss-2515", "vid":"Victonator-2131",
               "dirk":"Ardipithecus-2952","aika":"AikaNoodle-2123","jordy":"AikaNoodle-2123",
                  "niels":"Che-21446","che":"Che-21446"}
    if profilename.lower() in nameToUser:
        profilename=nameToUser[profilename.lower()]

    async with aiohttp.ClientSession() as session:
        async with session.get("https://ow-api.com/v1/stats/pc/eu/" + profilename + "/complete") as r:
            if r.status == 200:
                data = await r.json()

    if 'error' in data:
        message = "❕This profile does not exist❕"
        await ctx.send(message)
    elif data['ratings'] is None:
        message = "❕This profile does not have any competitive records for this season❕"
        await ctx.send(message)
    else:
        avalibleRoles = []
        for field in range(len(data['ratings'])):
            avalibleRoles.append(data['ratings'][field]['role'].lower())

        def makeEmbed(name, selectedRole, roleIcon, rankIcon, level):
            embed = discord.Embed(title=name, colour=discord.Colour(0xfa9c1d), timestamp=datetime.datetime.utcnow())
            embed.set_author(name=selectedRole, icon_url=roleIcon)
            embed.set_thumbnail(url=rankIcon)
            embed.add_field(name="Level", value=str(level) + " SR", inline=False)
            embed.set_footer(text="Made by Vic ♥ | ow-api.com")
            return (embed)

        def getData(field):
            name = data['name'].capitalize()
            selectedRole = data['ratings'][field]['role'].capitalize()
            roleIcon = data['ratings'][field]['roleIcon']
            rankIcon = data['ratings'][field]['rankIcon']
            level = data['ratings'][field]['level']
            return (name, selectedRole, roleIcon, rankIcon, level)
        if not avalibleRoles:
            message = "❕No competitive records found for this account❕"
            await ctx.send(message)
        else:
            if not len(role):
                embed = discord.Embed(title=data['name'].capitalize(), colour=discord.Colour(0xfa9c1d),
                                      timestamp=datetime.datetime.utcnow())
                embed.set_author(name='Full profile', icon_url=data['ratingIcon'])
                embed.set_thumbnail(url=data['icon'])
                embed.set_footer(text="Made by Vic ♥ | ow-api.com")
                for field in range(len(avalibleRoles)):
                    embed.add_field(name=avalibleRoles[field].capitalize(),
                                    value=str(data['ratings'][field]['level']) + " SR", inline=False)
                await ctx.send(embed=embed)
            else:
                if role[0].lower() == 'all':
                    embed = discord.Embed(title=data['name'].capitalize(), colour=discord.Colour(0xfa9c1d),
                                          timestamp=datetime.datetime.utcnow())
                    embed.set_author(name='Full profile', icon_url=data['ratingIcon'])
                    embed.set_thumbnail(url=data['icon'])
                    embed.set_footer(text="Made by Vic ♥ | ow-api.com")
                    for field in range(len(avalibleRoles)):
                        embed.add_field(name=avalibleRoles[field].capitalize(),
                                        value=str(data['ratings'][field]['level']) + " SR", inline=False)
                    await ctx.send(embed=embed)

                elif (role[0].lower() == 'tank' or role[0].lower() == 'defense') and 'tank' in avalibleRoles:
                    name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('tank'))
                    embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                    await ctx.send(embed=embed)

                elif (role[0].lower() == 'damage' or role[0].lower() == 'dps') and 'damage' in avalibleRoles:
                    name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('damage'))
                    embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                    await ctx.send(embed=embed)

                elif (role[0].lower() == 'support' or role[0].lower() == 'heal' or role[0].lower() == 'healer' or role[0].lower() == 'healing') and 'support' in avalibleRoles:
                    name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('support'))
                    embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                    await ctx.send(embed=embed)

                else:
                    message = "``" + str(role[0]) + "`` not found, try " + '``' + ', '.join(avalibleRoles) + '``'
                    await ctx.send(message)

@bot.command(name='update')
async def update(ctx):
    updateMessage = await ctx.send("Updating ranks")
    changePull.restart(updateMessage)

@bot.command(name='winky')
async def winky(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(source="winky.ogg", executable='ffmpeg/bin/ffmpeg.exe'),
                after=lambda e: print('winky played', e))
        await asyncio.sleep(1)
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("You're not connected to a voice chat")

@bot.command(name='mada')
async def mada(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(source="mada.ogg",executable='ffmpeg/bin/ffmpeg.exe'), after=lambda e: print('mada played', e))
        await asyncio.sleep(1)
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("You're not connected to a voice chat")

pullStatus = changePull.start()
bot.run(TOKEN)