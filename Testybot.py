import asyncio
import discord
import logging
import os
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from ThingyDo.DieRoll import *
from ThingyDo.Shout import shout
from ThingyDo.Info import *
from ThingyDo.Ascii import *
from ThingyDo.GetGreeting import *
from ThingyDo.DigimonIOAPI import *
from ThingyDo.TimeingDefinitions import *

intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD")
api_url = os.getenv("digimonAPI_search")

client = commands.Bot(command_prefix="?", intents=intents)
logging.basicConfig(filename=".\output.log", filemode="w", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

#
#Events
#

@client.event
async def on_error(event, *args, **kwargs):
	print("Here is the log \n ")
	print(traceback.format_exc())

@client.event
async def on_member_join(member):
	username = str(member.name)[:-5]
	channel = get_channel(os.getenv("DISCORD_GENERAL"))
	await channel.send(pickGreeting(username))



@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='with blocks'))
    
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))

#
#Commands
#

@client.command(pass_context=True)
async def roll(ctx):
	username = str(ctx.author)[:-5]
	message = ctx.message.content
	channel = ctx.channel
	await channel.send(dieRoll(username, message))
	await ctx.message.delete()

@client.command(pass_context=True)
async def yell(ctx):
	username = str(ctx.author)[:-5]
	channel = ctx.channel
	await channel.send(shout(username))
	await ctx.message.delete()

@client.command(pass_context=True)
async def test(ctx):
	username = str(ctx.author)[:-5]
	channel = ctx.channel
	await channel.send("Hello "+username)
	await ctx.message.delete()

@client.command(pass_context=True)
async def info(ctx):
	channel = ctx.channel
	await channel.send(giveInfo())	
	await ctx.message.delete()

@client.command(pass_context=True)
async def flip(ctx):
    channel = ctx.channel
    await channel.send(tblFlip())
    await ctx.message.delete()

@client.command(pass_context=True,name="search", aliases=["s", "lookup", "find", "f"])
async def search(ctx, arg):
	channel = ctx.channel
	await channel.send(searchInput(arg, api_url))

@client.command(pass_context=True, name="timing")
async def timing(ctx, message):
	channel=ctx.channel
	inTxt = ctx.message.content.split(" ")
	toSearch = str(' '.join(inTxt[1:]))
	await channel.send(pickTiming(toSearch))
	await ctx.message.delete()

@client.command(pass_context=True, name="schedule", aliases=['event'])
async def schedule(ctx):
	channel=ctx.channel
	inTxt = ctx.message.content.split(" ")
	happening = str(' '.join(inTxt[1:]))
	#month day time details
	await channel.send(scheduleEvent(happening))
	await ctx.message.delete()
	
client.run(TOKEN)