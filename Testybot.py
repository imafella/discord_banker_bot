import discord, asyncio, json
import logging
import os, traceback
from dotenv import load_dotenv
from ThingyDo.DieRoll import *
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection


#
#Discord bot setup
#
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
database = DatabaseConnection("discord_bot.db")
has_given_allowance_today = False

client = discord.Client(intents=intents)

logging.basicConfig(
	filename="output.log", 
	filemode="w", 
	level=logging.INFO, 
	format="%(asctime)s:%(levelname)s:%(message)s"
)
command_tree = discord.app_commands.CommandTree(client)

async def get_guild_channel_by_name(guild:discord.Guild, channel_name:str):
	"""
	Get a channel by name from a guild.
	"""
	for channel in guild.text_channels:
		if channel.name == channel_name:
			return channel
	return guild.system_channel
	# If no channel is found, return the system channel

#
# Timed things
#

async def change_presense_periodically():
	await client.wait_until_ready()
	while not client.is_closed():
		bot_activity = discord.Game(name=pickRandomActivity())
		await client.change_presence(activity=bot_activity, status=discord.Status.online)
		print(f"Changed presence to: Playing{bot_activity.name}")
		await asyncio.sleep(13 * 60 * 60)  # Change every 13 hours

async def change_avatar_periodically():
	await client.wait_until_ready()
	while not client.is_closed():
		await client.user.edit(avatar=utility.load_random_avatar())
		print(f"Changed avatar")
		await asyncio.sleep(14 * 60 * 60)  # Change every 14 hours

async def give_allowance():
	"""
	Give allowance to users every week on the specified day and time.
	Iterates through all guilds and users to give allowance, one guild at a time.
	"""
	await client.wait_until_ready()
	while not client.is_closed():
		await asyncio.sleep(6 * 60 * 60)  # every 6 hours check the day.
		if not utility.is_Allowance_Day and has_given_allowance_today:
			has_given_allowance_today = False
		elif utility.is_Allowance_Day and utility.is_past_Allowance_Time() and not has_given_allowance_today:
			allowance_list = database.get_allowance_info()
			if allowance_list is None or len(allowance_list) == 0:
				print("No allowance to be given.")
			else:
				allowance_list = utility.calculate_Allowance(allowance_list)
				for guild in allowance_list.keys():
						output="Today is allowance day! The following users have received their allowance:\n"
						database.give_allowance(allowance_info=allowance_list[guild])
						
						discord_guild = client.get_guild(int(guild))
						if discord_guild is None:
							discord_guild = await client.fetch_guild(int(guild))
							if discord_guild is None:
								print(f"Guild not found: {guild}")
								continue

						currency_symbol = database.get_guild_currency_details(guild_id=int(guild))[3]

						for account in allowance_list[guild]:
							member = discord_guild.get_member(account['user_id'])
							if member is None:
								member = await discord_guild.fetch_member(account['user_id'])
								if member is None:
									print(f"Member not found: {account['user_id']}")
									continue
							
							output += f"{member.mention} has received {currency_symbol}{account['amount']} for their allowance.\n"
						channel = get_guild_channel_by_name(discord_guild, "banking")
						if channel is None:
							channel = discord_guild.system_channel
						channel.send(output)
						print(output)
						asyncio.sleep(5)
						# Give the bot a break between messages
			has_given_allowance_today = True

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
		app_command_list = await command_tree.sync()
		print(f"The Following commands have been synced:\n")
		for command in app_command_list:
			print(f"{command.name} - {command.description}\n")
	except discord.HTTPException as e:
		print(f"Failed to sync command tree: {e}")
		logging.error("Failed to sync command tree: %s", e)

	client.loop.create_task(change_presense_periodically())
	client.loop.create_task(change_avatar_periodically())
	client.loop.create_task(give_allowance())

	print("Hello, I am online!")
	print('Connected to bot: {}'.format(client.user.name))
	print('Bot ID: {}'.format(client.user.id))

@client.event
async def on_user_update(before:discord.User, after:discord.User):
	if (before.avatar != after.avatar or before.display_avatar != after.display_avatar) and before.id != client.user.id:
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
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=dieRoll(username, dice, modifier) )

@command_tree.command(name="yell",description="Yell something.")
async def yell(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=shout(username))


@command_tree.command(name="test",description="this is for testing. Leave it alone.")
async def test(interaction: discord.Interaction, member:discord.Member):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=f"Hello {username}, I am a test command. You also mentioned {member.mention}. Don't do that.")

@command_tree.command(name="flip",description="Flips the table")
async def flip(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	await interaction.response.send_message(content=tblFlip())

@command_tree.command(name="info",description="Info about the bot.")
async def info(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	await interaction.response.send_message(content=giveInfo())

@command_tree.command(name="good_bot",description="Tell the bot it's a good bot.")
async def good_bot(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=pickRandomGoodBotResponse(username))

#
#Banking commands
#

@command_tree.command(name="join_bank",description="Make a bank account. Join the server bank. One of us.")
async def join_bank(interaction: discord.Interaction):

	# Acknowledge the interaction immediately
	await interaction.response.defer()

	username = interaction.user.id
	if interaction.guild is None:
		await interaction.followup.send(content="You need to be in a server to join the bank.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id):
		database.set_up_guild_bank(guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the user is already in the bank
	if database.is_user_in_guild_bank(username, guild_id):
		bank_account = database.get_user_bank_account_details(user_id=username, guild_id=guild_id)
		await interaction.followup.send(content=pickRandomYouAlreadyHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
		return
	
	if database.is_user_bank_account_archived(username, guild_id):
		did_the_thing = database.unarchive_user_bank_account(user_id=username, guild_id=guild_id)
	else:
		did_the_thing = database.add_user_to_guild_bank(user_id=username, guild_id=guild_id)
	if not did_the_thing:
		await interaction.followup.send(content="I broke myself trying to add you to the bank.")
		return
	
	bank_account = database.get_user_bank_account_details(user_id=username, guild_id=guild_id)
	
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

	
	await interaction.followup.send(content=pickRandomBankWelcomeResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
	return


@command_tree.command(name="bank_balance",description="Get your bank balance.")
async def bank_balance(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	user_id = interaction.user.id
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to check your bank balance.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id):
		database.set_up_guild_bank(guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the user is already in the bank
	if not database.is_user_in_guild_bank(user_id, guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	bank_account = database.get_user_bank_account_details(user_id, guild_id)
	if bank_account is None:
		await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
		return
	
	await interaction.response.send_message(content=pickRandomBankBalanceResponse(username=interaction.user.mention, bank_balance=bank_account[3], currency_name=guild_currency[2], currency_symbol=guild_currency[3]))

@command_tree.command(name="leave_bank",description="Close your bank account.")
async def leave_bank(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	user_id = interaction.user.id
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to close your bank account.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the user is already in the bank
	if not database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
	
	did_the_thing = database.remove_user_from_guild_bank(guild_id= guild_id,user_id=user_id)
	if not did_the_thing:
		await interaction.response.send_message(content=f"I broke myself trying to remove you from the bank. I blame you, {interaction.user.mention}.")
		return
	
	await interaction.response.send_message(content=pickRandomLeavingTheBankResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))

@command_tree.command(name="get_change_costs",description="Get the costs of changing the currency name and symbol.")
async def get_change_costs(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to get the change costs.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)
	guild_currency_change_costs = database.get_change_costs(guild_id=guild_id)
	if guild_currency_change_costs is None:
		await interaction.response.send_message(content="I broke myself trying to get the change costs.")
		return
	
	await interaction.response.send_message(content=pickRandomChangeCostResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], name_cost=guild_currency_change_costs[2], symbol_cost=guild_currency_change_costs[3]))

@command_tree.command(name="change_currency_name",description="Change the currency name.")
async def change_currency_name(interaction: discord.Interaction, new_currency_name:str):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to change the currency name.")
		return
	guild_id = interaction.guild.id
	user_id=interaction.user.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	if len(new_currency_name) > 50:
		await interaction.response.send_message(content="The currency name can't be longer than 50 characters.")
		return

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)
	guild_currency_change_costs = database.get_change_costs(guild_id=guild_id)

	if new_currency_name.strip() == "":
		await interaction.response.send_message(content="The currency name can't be empty.")
		return

	# Check if new currency name contains letters
	if not any(char.isalpha() for char in new_currency_name):
		await interaction.response.send_message(content="The currency name must contain at least one letter.")
		return

	if guild_currency[2] == new_currency_name:
		#TODO pickRandomThatChangesNothingResponse
		await interaction.response.send_message(content="The currency name is already set to that ya daft monkey.")
		return
	
	if guild_currency_change_costs is None:
		await interaction.response.send_message(content="I broke myself trying to get the change costs.")
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
	if bank_account is None:
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	if bank_account[3] < guild_currency_change_costs[2]:
		#TODO pickRandomYouDontHaveEnoughMoneyResponse
		await interaction.response.send_message(content="You don't have enough money to change the currency name.")
		return
	
	did_the_thing = database.change_currency_name(guild_id=guild_id, new_name=new_currency_name, user_id=user_id, cost=guild_currency_change_costs[2], balance=bank_account[3])
	if not did_the_thing:
		await interaction.response.send_message(content="I broke myself trying to change the currency name.")
		return
	#TODO pickRandomChangeCurrencyNameResponse
	await interaction.response.send_message(content=f"Changed the currency name to {new_currency_name}.")

@command_tree.command(name="change_currency_symbol",description="Change the currency symbol.")
async def change_currency_symbol(interaction: discord.Interaction, new_currency_symbol:str):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to change the currency symbol.")
		return
	guild_id = interaction.guild.id
	user_id=interaction.user.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)
	guild_currency_change_costs = database.get_change_costs(guild_id=guild_id)

	if new_currency_symbol.strip() == "":
		await interaction.response.send_message(content="The currency symbol can't be empty.")
		return
	
	if len(new_currency_symbol) > 50:
		await interaction.response.send_message(content="The currency symbol can't be longer than 50 characters.")
		return

	if guild_currency[3] == new_currency_symbol:
		#TODO pickRandomThatChangesNothingResponse
		await interaction.response.send_message(content="The currency symbol is already set to that ya daft monkey.")
		return
	
	if guild_currency_change_costs is None:
		await interaction.response.send_message(content="I broke myself trying to get the change costs.")
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
	if bank_account is None:
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	if bank_account[3] < guild_currency_change_costs[3]:
		#TODO pickRandomYouDontHaveEnoughMoneyResponse
		await interaction.response.send_message(content="You don't have enough money to change the currency symbol.")
		return
	
	did_the_thing = database.change_currency_symbol(guild_id=guild_id, new_symbol=new_currency_symbol, user_id=user_id, cost=guild_currency_change_costs[3], balance=bank_account[3])
	if not did_the_thing:
		await interaction.response.send_message(content="I broke myself trying to change the currency symbol.")
		return
	#TODO pickRandomChangeCurrencySymbolResponse
	await interaction.response.send_message(content=f"Changed the currency symbol to {new_currency_symbol}.")

#TODO transfer_money
@command_tree.command(name="transfer_money",description="Transfer money to another user.")
async def transfer_money(interaction: discord.Interaction, user:discord.User, amount:float):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to transfer money.")
		return
	guild_id = interaction.guild.id
	user_id=interaction.user.id

	if amount < 0:
		await interaction.response.send_message(content="You can't transfer a negative amount of money.")
		return
	if amount == 0:
		await interaction.response.send_message(content="You can't transfer 0.")
		return

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the user is already in the bank
	if not database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	# Check is target user is in the bank
	if not database.is_user_in_guild_bank(user.id, guild_id=guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
	if bank_account is None:
		await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
		return
	
	if bank_account[3] < amount:
		#TODO pickRandomYouDontHaveEnoughMoneyResponse
		await interaction.response.send_message(content="You don't have enough money to transfer.")
		return
	
	did_the_thing = database.transfer_money(guild_id=guild_id, sender_user_id=user_id, receiver_user_id=user.id, amount=amount)
	if not did_the_thing:
		await interaction.response.send_message(content="I broke myself trying to transfer money.")
		return
	#TODO pickRandomTransferMoneyResponse
	await interaction.response.send_message(content=f"Transferred {amount} {guild_currency[3]}s from {interaction.user.mention} to {user.mention}.")
#TODO give_allowance. weekly increase balance if member has used imabot (not banking functions) in the last week

@command_tree.command(name="award",description="Award money to a user.")
async def award(interaction: discord.Interaction, user:discord.User, amount:float):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to award money.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the awarding user is an admin
	if interaction.user.id not in admins:
		await interaction.response.send_message(content=f"{interaction.user.mention}, You are not allowed to award money.")
		return
	
	# Check is target user is in the bank
	if not database.is_user_in_guild_bank(user.id, guild_id=guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user.id, guild_id=guild_id)
	if bank_account is None:
		await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
		return
	
	did_the_thing = database.award_money(guild_id=guild_id, user_id=user.id, amount=amount)
	if not did_the_thing:
		await interaction.response.send_message(content="I broke myself trying to award money.")
		return
	#TODO pickRandomAwardMoneyResponse
	await interaction.response.send_message(content=f"Awarded {amount} {guild_currency[3]}s to {user.mention}.")

@command_tree.command(name="set_bank_balance",description="Set the bank balance of a user.")
async def set_bank_balance(interaction: discord.Interaction, user:discord.User, amount:float):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to set the bank balance.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)

	# Check if the awarding user is an admin
	if interaction.user.id not in admins:
		await interaction.response.send_message(content=f"{interaction.user.mention}, You are not allowed to set the bank balance.")
		return
	
	# Check is target user is in the bank
	if not database.is_user_in_guild_bank(user.id, guild_id=guild_id):
		await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
		return
	
	bank_account = database.get_user_bank_account_details(user_id=user.id, guild_id=guild_id)
	if bank_account is None:
		await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
		return
	
	did_the_thing = database.set_bank_balance(guild_id=guild_id, user_id=user.id, amount=amount)
	if not did_the_thing:
		await interaction.response.send_message(content="I broke myself trying to set the bank balance.")
		return
	#TODO pickRandomSetBankBalanceResponse
	await interaction.response.send_message(content=f"Set {user.mention}'s bank balance to {amount}.")

@command_tree.command(name="get_currency_details",description="Get the currency details.")
async def get_currency_details(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	if interaction.guild is None:
		await interaction.response.send_message(content="You need to be in a server to get the currency details.")
		return
	guild_id = interaction.guild.id

	# Check if the guild has its own bank
	if not database.is_guild_bank_setup(guild_id=guild_id):
		database.set_up_guild_bank(guild_id=guild_id)

	guild_currency = database.get_guild_currency_details(guild_id=guild_id)
	if guild_currency is None:
		await interaction.response.send_message(content="I broke myself trying to get the currency details.")
		return
	
	await interaction.response.send_message(content=f"The currency name is {guild_currency[2]} and the symbol is {guild_currency[3]}.")

#Runs the bot		
client.run(TOKEN)