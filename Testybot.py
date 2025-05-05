import discord
import logging
import os, traceback
from dotenv import load_dotenv
from ThingyDo.DieRoll import *
from ThingyDo.Messages import *


#
#Discord bot setup
#
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD")
main_entry_channel = os.getenv("DISCORD_MAIN_ENTRY_CHANNEL")

client = discord.Client(intents=intents)

logging.basicConfig(
	filename="output.log", 
	filemode="w", 
	level=logging.INFO, 
	format="%(asctime)s:%(levelname)s:%(message)s"
)
command_tree = discord.app_commands.CommandTree(client)

#
#Events
#

@client.event
async def on_error(event, *args, **kwargs):
	logging.error("An error occurred in event: %s", event)
	logging.error("Error details:\n%s", traceback.format_exc())

@client.event
async def on_member_join(member:discord.Member):
	username = member.mention
	channel = member.guild.system_channel
	if channel:
		await channel.send(pickGreeting(username))

@client.event
async def on_ready():
	try:
		await command_tree.sync()
		print("Command tree synced globally.")
	except discord.HTTPException as e:
		print(f"Failed to sync command tree: {e}")
		logging.error("Failed to sync command tree: %s", e)
	bot_activity = discord.Game(name="with reality")
	await client.change_presence(activity=bot_activity, status=discord.Status.online)
	channel = client.get_channel(int(main_entry_channel))
	# Send a message to the channel when the bot is ready
	if channel:
		# await channel.send("Hello, I am online!")
		print("Hello, I am online!")
	else:
		logging.error("Channel not found: %s", int(main_entry_channel))
		print(f"Channel not found: {int(main_entry_channel)}\n{channel}")
	print('Connected to bot: {}'.format(client.user.name))
	print('Bot ID: {}'.format(client.user.id))

@client.event
async def on_user_update(before:discord.User, after:discord.User):
	if before.avatar != after.avatar or before.display_avatar != after.display_avatar:
		channel = after.mutual_guilds[0].system_channel
		if channel:
			await channel.send(pickRandomAvatarCompliment(after.mention))
		else:
			logging.error("Mutual Channel not found")
			print(f"Mutual Channel not found")

@client.event
async def on_member_update(before:discord.Member, after:discord.Member):
	if before.avatar != after.avatar or before.display_avatar != after.display_avatar:
		channel = after.guild.system_channel
		if channel:
			await channel.send(pickRandomAvatarCompliment(after.mention))
		else:
			logging.error("Mutual Channel not found")
			print(f"Mutual Channel not found")
	

#
#Commands
#

@command_tree.command(name="roll",description="Roll a die. XdY + Z")
async def roll(interaction: discord.Interaction, dice:str, modifier:int=0):
	username = interaction.user.mention
	await interaction.response.send_message(content=dieRoll(username, dice, modifier) )

@command_tree.command(name="yell",description="Yell something.")
async def yell(interaction: discord.Interaction):
	username = interaction.user.mention
	await interaction.response.send_message(content=shout(username))


@command_tree.command(name="test",description="this is for testing. Leave it alone.")
async def test(interaction: discord.Interaction):
	username = interaction.user.mention
	await interaction.response.send_message(content="Hello "+username)

@command_tree.command(name="flip",description="Flips the table")
async def flip(interaction: discord.Interaction):
	await interaction.response.send_message(content=tblFlip())

@command_tree.command(name="info",description="Info about the bot.")
async def info(interaction: discord.Interaction):
	await interaction.response.send_message(content=giveInfo())

@command_tree.command(name="good_bot",description="Tell the bot it's a good bot.")
async def good_bot(interaction: discord.Interaction):
	username = interaction.user.mention
	await interaction.response.send_message(content=pickRandomGoodBotResponse(username))

#Runs the bot		
client.run(TOKEN)