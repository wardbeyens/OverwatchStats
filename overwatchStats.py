from discord.ext import commands
import discord
import json
import requests

TOKEN = open('token.txt').read()  # Get at discordapp.com/developers/applications/me

bot = commands.Bot(command_prefix='-')
# -----------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='hi', alias='hello')
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command(name='profile')
async def profile(ctx, profilename, roleSelected):
    url = "https://ow-api.com/v1/stats/pc/eu/"
    url = url + profilename + "/complete"
    r = requests.get(url)
    data = r.json()

    if 'error' in data:
        message="❕This profile does not exist❕"
        await ctx.send(message)
    else:
        avalibleRoles = []
        for field in range(len(data['ratings'])):
            avalibleRoles.append(data['ratings'][field]['role'].lower())

        def makeEmbed(name, role, roleIcon, rankIcon, level):
            embed = discord.Embed(title=name)
            embed.set_author(name=role, icon_url=roleIcon)
            embed.set_thumbnail(url=rankIcon)
            embed.add_field(name="Level", value=str(level) + " SR", inline=False)
            embed.set_footer(text="Made by Vic ♥")
            return (embed)

        def getData(field):
            name = data['name'].capitalize()
            role = data['ratings'][field]['role'].capitalize()
            roleIcon = data['ratings'][field]['roleIcon']
            rankIcon = data['ratings'][field]['rankIcon']
            level = data['ratings'][field]['level']
            return (name, role, roleIcon, rankIcon, level)

        if not avalibleRoles:
            message = "❕No competitive records found for this account❕"
            await ctx.send(message)
        else:
            if roleSelected.lower() == '' or roleSelected.lower() == 'all':
                embed = discord.Embed(title=data['name'].capitalize())
                embed.set_author(name='Full profile', icon_url=data['ratingIcon'])
                embed.set_thumbnail(url=data['icon'])
                embed.set_footer(text="Made by Vic ♥")
                for field in range(len(avalibleRoles)):
                    embed.add_field(name=avalibleRoles[field].capitalize(),
                                    value=str(data['ratings'][field]['level']) + " SR", inline=False)
                await ctx.send(embed=embed)

            elif roleSelected.lower() == ('tank') and 'tank' in avalibleRoles:
                name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('tank'))
                embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                await ctx.send(embed=embed)

            elif roleSelected.lower() == ('damage' or roleSelected.lower() == 'dps') and 'damage' in avalibleRoles:
                name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('damage'))
                embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                await ctx.send(embed=embed)

            elif roleSelected.lower() == (
                    'support' or roleSelected.lower() == 'heal' or roleSelected.lower() == 'healer' or roleSelected.lower() == 'healing') and 'support' in avalibleRoles:
                name, role, roleIcon, rankIcon, level = getData(avalibleRoles.index('support'))
                embed = makeEmbed(name, role, roleIcon, rankIcon, level)
                await ctx.send(embed=embed)

            else:
                message = str(roleSelected.capitalize()) + " not found, try " + ', '.join(avalibleRoles)
                await ctx.send(message)

bot.run(TOKEN)