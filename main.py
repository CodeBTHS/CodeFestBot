import dotenv
dotenv.load_dotenv(verbose=True)
import os
import chalk
import discord
from discord.ext import commands
from tinydb import TinyDB, Query, where
import log

db = TinyDB("db.json")
teams_table = db.table("teams")
users_table = db.table("users")

bot = commands.Bot(command_prefix="cf!")
bot.remove_command('help')
# bot.remove_command("help")
token = os.getenv("TOKEN")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("in CodeFest 2021"))
    log.good("Bot is ready!")

@bot.command()
async def help(ctx: commands.Context):
    embed = discord.Embed(title="Help Menu", description="`cf!help` — Shows this help message\n`cf!teams` — List teams\n`cf!create_team <team name>` — Create a team\n`cf!remove_team <team name>` — Remove a team\n`cf!join <team name>` — Join a team\n`cf!leave` — Leave your current team", color=0x63e2ff)
    await ctx.channel.send(embed=embed)

# TEAM MANAGEMENT
@bot.command()
@commands.has_role("Executives")
async def create_team(ctx: commands.Context, *, team_name: str):
    teams_table.insert({'name': team_name})
    await ctx.channel.send(embed=discord.Embed(title=f"Team **{team_name}** has been created.", color=0x63e2ff))
    log.good(f"Team \"{team_name}\" has been created.")

@bot.command()
@commands.has_role("Executives")
async def teams(ctx: commands.Context):
    teams = teams_table.all()
    embed = discord.Embed(title="Team List", color=0x63e2ff)

    for team in teams:
        members = users_table.search(where('team') == team['name'])
        members_string = ""
        for member in members:
            members_string = members_string + bot.get_user(member['id']).name + ", "
        if len(members_string) == 0:
            members_string = "No members"
        embed.add_field(name=team['name'], value=members_string)

    await ctx.channel.send(embed=embed)
    log.good("Listed teams.")

@bot.command()
@commands.has_role("Executives")
async def remove_team(ctx: commands.Context, *, team_name: str):
    teams_table.remove(where('name') == team_name)
    await ctx.channel.send(embed=discord.Embed(title=f"Team **{team_name}** has been removed.", color=0x63e2ff))
    log.good(f"Team \"{team_name}\" has been removed.")

# USER MANAGEMENT
@bot.command()
async def join(ctx: commands.Context, *, team_name: str):
    teams = teams_table.search(where('name') == team_name)
    users = users_table.search(where('id') == ctx.author.id)

    if(len(teams) == 0):
        await ctx.channel.send(embed=discord.Embed(title=f"Team **{team_name}** was not found.", color=0x63e2ff))
        return
    
    if(len(users) == 0):
        users_table.insert({'id': ctx.author.id, 'team': team_name})
        await ctx.channel.send(embed=discord.Embed(title=f"You have joined **{team_name}**.", color=0x63e2ff))
    else:
        users[0].update({'team': team_name})
        await ctx.channel.send(embed=discord.Embed(title=f"You have joined **{team_name}**.", color=0x63e2ff))

@bot.command()
async def team(ctx: commands.Context):
    users = users_table.search(where('id') == ctx.author.id)
    if(len(users) == 0):
        await ctx.channel.send(embed=discord.Embed(title=f"You are not in a team.", color=0x63e2ff))
    else:
        await ctx.channel.send(embed=discord.Embed(title=f"You are in **{users[0]['team']}**.", color=0x63e2ff))

@bot.command()
async def leave(ctx: commands.Context):
    users = users_table.search(where('id') == ctx.author.id)
    if(len(users) == 0):
        await ctx.channel.send(embed=discord.Embed(title=f"You are not in a team.", color=0x63e2ff))
    else:
        users_table.remove(where('id') == ctx.author.id)
        await ctx.channel.send(embed=discord.Embed(title=f"You are no longer in **{users[0]['team']}**.", color=0x63e2ff))

bot.run(token)