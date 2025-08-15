import discord, asyncio, json, aiohttp
import logging, datetime
from zoneinfo import ZoneInfo
import os, traceback
from dotenv import load_dotenv
from ThingyDo.DieRoll import *
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection
from Connections.malConnection import MALConnection
from CommandTrees.Bank import Bank
from CommandTrees import Roulette_Bet
from CommandTrees.lotto import Lotto
from CommandTrees.digimon_card import Card
from Connections.GPT_Connection import GPTConnection
from urlextract import URLExtract
import argparse
from models.bank_account import bank_account as BankAccount


#
#Discord bot setup
#
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
Test_TOKEN = os.getenv("DISCORD_TESTING_TOKEN")
admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
ignore_these_user_msgs = json.loads(os.getenv("ignore_user_msgs", "[]"))
ignore_these_user_reactions = json.loads(os.getenv("ignore_user_reactions", "[]"))
MAIN_ID = os.getenv("ID")
TEST_ID = os.getenv("TEST_ID")
database = DatabaseConnection(os.getenv('DB_PATH'))
mal_connection = MALConnection()
has_given_allowance_today = False
extractor = URLExtract()

client = discord.Client(intents=intents)

logging.basicConfig(
	filename="output.log", 
	filemode="w", 
	level=logging.INFO, 
	format="%(asctime)s:%(levelname)s:%(message)s"
)
command_tree = discord.app_commands.CommandTree(client)
bank = Bank()
command_tree.add_command(bank)
roulette = Roulette_Bet.Roulette()
command_tree.add_command(roulette)
roulette_tasks = {}
lotto = Lotto()
command_tree.add_command(lotto)
lotto_tasks = {}
digimon_card = Card()
command_tree.add_command(digimon_card, guild=discord.Object(id=int(os.getenv("DIGIMON_GUILD_ID", "0"))))
tyler_bot_config = utility.load_config("tyler_bot")
tyler_bot = GPTConnection(name=tyler_bot_config["name"], instructions=tyler_bot_config["instructions"], model=tyler_bot_config["model"])


async def get_guild_channel_by_name(guild:discord.Guild, channel_name:str):
	"""
	Get a channel by name from a guild.
	"""
	for channel in guild.text_channels:
		if channel.name == channel_name:
			return channel
	return guild.system_channel
	# If no channel is found, return the system channel

async def get_random_guild_member(guild:discord.Guild) -> discord.Member:
	"""
	Get a random member from a guild.
	"""
	members = [member for member in guild.members if not member.bot]
	if members:
		return random.choice(members)
	else:
		return None
	# If no members are found, return None

async def has_sent_message_today(channel: discord.TextChannel, search_string: str, client: discord.Client) -> bool:
	now = datetime.datetime.now(ZoneInfo("America/St_Johns"))
	today = now.date()
	async for message in channel.history(limit=800):  # Adjust limit as needed
		if (message.author == client.user or message.author.id in ignore_these_user_msgs) and message.created_at.date() == today:
			# Check plain text content for the search string
			if search_string in message.content :          
				return True
			for embed in message.embeds:
				# Check embed title and description for the search string
				if (embed.title and search_string in embed.title) or (embed.description and search_string in embed.description):
					return True
	return False



async def get_anime_id(mal_url:str) -> int:
	"""
	Extract the anime ID from a MyAnimeList URL.
	Example URLs:
	- https://myanimelist.net/anime/205/Samurai_Champloo
	- https://myanimelist.net/anime/205
	"""
	if "myanimelist.net/anime/" in mal_url:
		try:
			return int(mal_url.split("myanimelist.net/anime/")[1].split("/")[0].split(" ")[0])
		except ValueError:
			return None
	else:
		return None

async def get_image(path:str) -> bytes:
	"""
	Get the image bytes from a file path.
	"""
	image_path = os.path.expanduser(path)  # Adjust filename as needed

	if image_path != None and not os.path.exists(image_path):
		return None
        
	return open(image_path, 'rb').read()

async def get_bot_equivilant_emoji(emoji_name:str) -> str:
	"""
	Get the bot emoji as a string.
	"""
	watched_emoji_names = utility.load_config("emojis")['watched_emoji']

	bot_emoji_name = emoji_name
	if emoji_name in watched_emoji_names:
		# If the emoji is in the watched emoji list, return the bot equivalent emoji
		if bot_emoji_name in ["angry", "rage", "anger","😡","😠", "💢" ]:
			bot_emoji_name = "angry"
		elif bot_emoji_name in ["laughing", "joy","rotfl","😂","🤣","😆"]:
			bot_emoji_name = "laugh"
		elif bot_emoji_name in ["thumbsdown", "👎"]:
			bot_emoji_name = "thumb_down"
		elif bot_emoji_name in ["thumbsup","👍"]:
			bot_emoji_name = "thumb_up"
		elif bot_emoji_name in ["heart", "hearts","❤️","♥️",]:
			bot_emoji_name = "heart"
		elif bot_emoji_name in ["100", "hundred","💯"]:
			bot_emoji_name = "100"
		elif bot_emoji_name in ["open_mouth", "astonished", "😮","😲"]:
			bot_emoji_name = "open_mouth"
		bot_emoji_name = f"bot_{bot_emoji_name}"
	return bot_emoji_name

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
	while not client.is_closed() and str(client.application_id) != TEST_ID:
		await client.user.edit(avatar=utility.load_random_avatar())
		print(f"Changed avatar")
		await asyncio.sleep(14 * 60 * 60)  # Change every 14 hours

async def roulette_game(guild_id:int):
	await client.wait_until_ready()
	while not client.is_closed():
		# await asyncio.sleep(15*2)
		await asyncio.sleep(2*60)
		# print(f"Checking for roulette bets")
		# Check if there are any roulette bets to process
		roulette_bets = database.get_placed_guild_roulette_bets(guild_id=guild_id)
		if roulette_bets is None or len(roulette_bets) == 0:
			# print("No roulette bets to process.")
			continue
		print(f"In Guild: {guild_id}, Found {len(roulette_bets)} roulette bets to process.")
		guild = client.get_guild(guild_id)
		channels = guild.text_channels
		target_channel = None
		for channel in channels:
			if channel.name == "casino":
				target_channel = channel
				break
		if target_channel is None:
			print(f"No casino channel found in guild: {guild_id}.")
			continue

		# --- Embed timer logic ---
		timer_seconds = 120
		# timer_seconds = 30
		embed = discord.Embed(
            title="Roulette Wheel Spinning Soon!",
            description=f"⏳ Time remaining: **{timer_seconds // 60}:{timer_seconds % 60:02d}**",
            color=discord.Color.gold()
        )
		embed.set_footer(text="Place your bets now!")
		message = await target_channel.send(embed=embed)

		for remaining in range(timer_seconds - 1, -1, -1):
			await asyncio.sleep(1)
			if remaining % 10 == 0 or remaining < 10:  # Update every 10s, then every second for last 10s
				embed.description = f"⏳ Time remaining: **{remaining // 60}:{remaining % 60:02d}**"
				await message.edit(embed=embed)

		embed.description = "⏰ **Last call is over.**"
		embed.set_footer(text="The roulette wheel will spin shortly.")
		await message.edit(embed=embed)

		# --- End of embed timer logic ---
		# Process the roulette bets
		black_emoji = "⚫"
		red_emoji = "🔴"
		green_emoji = "🟢"
		number = 0
		color = "green"  # Start with green for the wheel
		emoji_color = await roulette.get_roulette_roll_color(roll=0,use_emojis=True)
		wheel = discord.Embed(
            title="Roulette Wheel!",
            description=f"{number}-{emoji_color}",
            color=discord.Color.gold()
        )
		wheel.set_footer(text="Spinning the wheel...")
		spin_msg = await target_channel.send(embed=wheel)
		# Simulate the spinning of the wheel
		for i in range(random.randint(10,60)):
			await asyncio.sleep(0.5)
			number += random.randint(1, 3)
			if number > 36:
				number = 0	
			emoji_color = await roulette.get_roulette_roll_color(roll=number,use_emojis=True)
			wheel.description = f"{number}-{emoji_color}"
			await spin_msg.edit(embed=wheel)
		await asyncio.sleep(0.5)
		wheel.set_footer(text="The wheel is slowing down...")
		await spin_msg.edit(embed=wheel)
		for i in range(random.randint(5,15)):
			await asyncio.sleep(1.5)
			number += random.randint(1, 3)
			if number > 36:
				number = 0	
			emoji_color = await roulette.get_roulette_roll_color(roll=number,use_emojis=True)
			wheel.description = f"{number}-{emoji_color}"
			await spin_msg.edit(embed=wheel)
		await asyncio.sleep(1)

		# Then send the result as usual
		number = await roulette.roll_roulette()
		color = await roulette.get_roulette_roll_color(roll=number)
		emoji_color = await roulette.get_roulette_roll_color(roll=number,use_emojis=True)
		result = {"number": number, "color": color}
		
		wheel.description = f"{number}-{emoji_color}"
		
		wheel.set_footer(text="The wheel has stopped spinning!")
		await spin_msg.edit(embed=wheel)		

		bets = database.get_placed_guild_roulette_bets(guild_id=guild_id)

		bet_results = discord.Embed(
            title="Roulette Bet Results!",
            description=f"",
            color=discord.Color.gold()
        )

		bet_output = ""
		guild_currency = database.get_guild_currency_details(guild_id=guild_id)
		currency_name = guild_currency.name if guild_currency else "currency"
		currency_symbol = guild_currency.symbol if guild_currency else "$"
		for bet in bets:
			username = guild.get_member(bet['user_id']).mention
			try:
				bet_outcome = await roulette.apply_roulette_results(guild_id=guild_id, bet=bet, result=result)
				account = database.get_user_bank_account_details(user_id=bet['user_id'], guild_id=guild_id)
				balance = account.balance if account else 0
				if bet_outcome[1]: # A win
					bet_output += f"{username} won {bet_outcome[0]} for betting {bet['type']} on {bet['input']} with a bet of {bet['amount']}! New Balance of: {balance} {currency_name}s\n"
				else:  # A loss
					bet_output += f"{username} lost {bet['amount']} for betting {bet['type']} on {bet['input']}. New Balance of: {balance} {currency_name}s\n"
			except Exception as e:
				print(f"Error processing bet for user {bet['user_id']}: {e}")
				traceback.print_exc()
				continue

		bet_results.description = bet_output if bet_output else "No bets were placed or all bets lost."
		bet_results.set_footer(text="Thank you for playing!")

		await target_channel.send(embed=bet_results)

async def start_roulette_task(guild_id:int):
    """
    Start the roulette task for a specific guild.
    """
    global roulette_tasks
    # If the task is not running or is done, start a new one
    if guild_id not in roulette_tasks or roulette_tasks[guild_id].done():
        task = asyncio.create_task(roulette_game(guild_id=guild_id))
        roulette_tasks[guild_id] = task
        print(f"Started roulette task for guild: {guild_id}")
    else:
        print(f"Roulette task already running for guild: {guild_id}")

async def classic_lotto_game(guild_id:int):
	"""
	Classic Lotto game for a specific guild.
	"""
	await client.wait_until_ready()
	while not client.is_closed():
		await asyncio.sleep(2 * 60 * 60)  # Check every 2 hours

		# checks for casino channel
		channels = client.get_guild(guild_id).text_channels
		if channels is None or len(channels) == 0:
			print(f"No text channels found in guild: {guild_id}.")
			continue
		target_channel = None
		for channel in channels:
			if channel.name == "casino":
				target_channel = channel
				break
		if target_channel is None:
			print(f"No casino channel found in guild: {guild_id}.")
			continue

		# Post ad for tomorrow classic lotto
		if (utility.check_if_day(0) or utility.check_if_day(3)) and utility.check_if_past_time(16):
			await lotto_ad(guild_id=guild_id, target_channel=target_channel, title="Classic Lotto Ad!", description="Classic lotto being drawn tomorrow! Get your tickets now!", footer="use '/lotto buy_classic_ticket' to get your ticket!", color=discord.Color.red())
			continue

		# check if today is Tuesday or Friday
		if not utility.is_classic_lotto_draw_day():  # or not utility.is_past_classic_lotto_draw_time()
			print(f"Today is not a classic lotto day for guild: {guild_id}. Skipping.")
			continue

		

		if utility.is_classic_lotto_draw_day() and not utility.is_past_classic_lotto_draw_time():
			continue  # If it's a draw day but not past the draw time, skip the draw

		# Check if there are any classic lotto tickets to process
		tickets = database.get_guild_typed_active_lotto_tickets(guild_id=guild_id, ticket_type=1)
		if tickets is None or len(tickets) == 0:
			print("No classic lotto tickets to process.")
			continue

		# check if the lotto has already been drawn today
		has_already_drawn = await has_sent_message_today(channel=target_channel, search_string="Classic Lotto Draw!", client=client)
		if has_already_drawn:
			print(f"Classic lotto draw has already been done today for guild: {guild_id}. Skipping.")
			continue

		await lotto_ad(guild_id=guild_id, target_channel=target_channel, title="Classic Lotto Ad!", description="Classic lotto being drawn today in 2 hours! Get your tickets now!", footer="use '/lotto buy_classic_ticket' to get your ticket!", color=discord.Color.red())
		
		await asyncio.sleep(2 * 60 * 60)
		
		# If we have tickets, process them
		print(f"In Guild: {guild_id}, Found {len(tickets)} classic lotto tickets to process.")
		# Do the lotto draw
		classic_lotto_draw = await lotto.generate_classic_lotto_draw() # This way no late tickets are processed.
		lotto_game_details = utility.load_config("lotto_config")["1"]  # Get the game type details
		guild_currency = database.get_guild_currency_details(guild_id=guild_id)
		if guild_currency is None:
			print(f"Guild currency not found for guild: {guild_id}.")
			continue

		game_results = ""
		for ticket in tickets:
			user = client.get_user(ticket['user_id'])
			if user is None:
				try:
					user = await client.fetch_user(ticket['user_id'])
				except discord.NotFound:
					print(f"User not found: {ticket['user_id']}")
					continue			
			
			# Process the ticket
			matches = await lotto.check_ticket_matches(ticket_type=1, ticket_numbers=ticket['ticket_numbers'].split(','), draw_numbers=classic_lotto_draw)
			winnings = lotto_game_details['matches'][str(matches)]['winnings']
			database.set_lotto_ticket_results(guild_id=guild_id, user_id=user.id, ticket_id=ticket['id'], matches=matches, winnings=winnings)
			bank_account = database.get_user_bank_account_details(user_id=user.id, guild_id=guild_id)
			if bank_account is None:
				print(f"Bank account not found for user: {user.id} in guild: {guild_id}")
				continue

			new_balance_msg = f"New Balance: {guild_currency.symbol}{bank_account.balance}"
			if matches == 0:
				game_results += f"{user.mention} did not win with ticket: {ticket['ticket_numbers']}. {new_balance_msg}\n"
			elif str(matches) == list(lotto_game_details['matches'].keys())[0]: # This is the jackpot match
				game_results += f"{user.mention} won the jackpot of {winnings} with ticket: {ticket['ticket_numbers']} (Matched {matches} numbers). {new_balance_msg}\n"
			else:
				game_results += f"{user.mention} won {winnings} with ticket: {ticket['ticket_numbers']} (Matched {matches} numbers). Old Balance: {guild_currency.symbol}{bank_account.balance}\n"
		
		## -- Play the lotto draw -- ##
		lotto_draw = discord.Embed(
			title="Classic Lotto Draw!",
			description=f"Today's draw numbers are:",
			color=discord.Color.red()
		)
		lotto_draw.set_footer(text=f"Now Drawing for {lotto_game_details['name']}")

		# Send the draw numbers one by one
		message = await target_channel.send(embed=lotto_draw)

		for number in classic_lotto_draw:
			await asyncio.sleep(8)  # Give the bot a break between numbers
			lotto_draw.description += f" {number}"
			message = await message.edit(embed=lotto_draw)
		lotto_draw.set_footer(text=f"Draw complete for {lotto_game_details['name']}")
		await message.edit(embed=lotto_draw)
		## -- End Play the lotto draw -- ##

		## -- Display the lotto Results -- ##
		lotto_results = discord.Embed(
			title="Classic Lotto Results!",
			description=f"Today's results are:\n{game_results}",
			color=discord.Color.red()
		)
		lotto_draw.set_footer(text=f"Thanks for playing!")

		# Send the draw results
		await target_channel.send(embed=lotto_results)

async def lotto_ad(guild_id:int, target_channel:discord.TextChannel, title:str, description:str, footer:str,color:discord.Color):
	print(f"Posting Classic Lotto Ad for guild: {guild_id}")
	lotto_ad = discord.Embed(
				title=title,
				description=description,
				color=color
	)
	lotto_ad.set_footer(text=footer)
	# check if the ad has already been posted today
	has_already_done_ad = await has_sent_message_today(channel=target_channel, search_string=title, client=client)
	if not has_already_done_ad:
		await target_channel.send(embed=lotto_ad)
	else:
		print(f"{title} ad has already been done today for guild: {guild_id}. Skipping.")

async def start_classic_lotto_task(guild_id:int):
	"""
	Start the classic lotto task for a specific guild.
	"""
	global lotto_tasks
	# If the task is not running or is done, start a new one
	if "classic_lotto" not in lotto_tasks:
		lotto_tasks["classic_lotto"] = {}
	if guild_id not in lotto_tasks["classic_lotto"] or lotto_tasks["classic_lotto"][guild_id].done():
		task = asyncio.create_task(classic_lotto_game(guild_id=guild_id))
		lotto_tasks["classic_lotto"][guild_id] = task
		print(f"Started classic lotto task for guild: {guild_id}")
	else:
		print(f"Classic lotto task already running for guild: {guild_id}")

async def give_allowance():
	"""
	Give allowance to users every week on the specified day and time.
	Iterates through all guilds and users to give allowance, one guild at a time.
	"""
	await client.wait_until_ready()
	global has_given_allowance_today
	has_checked_once = False
	while not client.is_closed():
		
		if has_checked_once:
			await asyncio.sleep(6 * 60 * 60)  # every 6 hours check the day.
		if not has_checked_once:
			has_checked_once = True
		
		if not utility.is_Allowance_Day() and has_given_allowance_today:
			has_given_allowance_today = False
		elif utility.is_Allowance_Day() and utility.is_past_Allowance_Time() and not has_given_allowance_today:
			allowance_list = database.get_allowance_info()
			if allowance_list is None or len(allowance_list) == 0:
				print("No allowance to be given.")
			else:
				allowance_list = utility.calculate_Allowance(allowance_list)
				for guild in allowance_list.keys():
						
						print(f"Trying allowance for guild: {guild}")

						# Gets the Guild
						discord_guild = client.get_guild(int(guild))
						if discord_guild is None:
							try:
								discord_guild = await client.fetch_guild(int(guild))
								if discord_guild is None:
									print(f"Guild not found: {guild}")
									continue
							except Exception as e:
								print(f"Could not allowance for guild: {guild}")
								continue

						# Gets guild channel to send bank update in.
						channel = await get_guild_channel_by_name(discord_guild, "banking")
						if channel is None:
							channel = discord_guild.system_channel

						# Checks if the allowance has already been sent. If it has, skips that guild.
						if await has_sent_message_today(channel=channel, search_string="The following users have received their allowance",client=client):
							continue
						
						output="Today is allowance day! The following users have received their allowance:\n"
						
						currency_symbol = database.get_guild_currency_details(guild_id=int(guild)).symbol

						for account in allowance_list[guild]:
							member = discord_guild.get_member(account['user_id'])
							if member is None:
								member = await discord_guild.fetch_member(account['user_id'])
								if member is None:
									print(f"Member not found: {account['user_id']}")
									continue
							bank_account = database.get_user_bank_account_details(user_id=account['user_id'], guild_id=guild)
							if bank_account is None:
								print(f"Bank account not found for user: {account['user_id']} in guild: {guild}")
								continue
							new_balance_msg = f"New Balance: {currency_symbol}{bank_account.balance+account['amount']}"
							
							output += f"{member.mention}:  Amount: {currency_symbol}{account['amount']}. Bot Usage: {account['bot_usage']} times. {new_balance_msg}\n"
						
						# Actually give out the allowance after numerous checks have been made.
						database.give_allowance(allowance_info=allowance_list[guild])

						await channel.send(output)
						print(output)
						await asyncio.sleep(5)
						# Give the bot a break between messages
			has_given_allowance_today = True

		

async def get_guild_emoji(guild:discord.Guild, emoji_name:str) -> discord.Emoji:
	"""
	Get a custom emoji from a guild by name.
	"""
	for emoji in guild.emojis:
		if emoji.name == emoji_name:
			return emoji
	return None
	# If no emoji is found, return None

#
#Events
#

@client.event
async def on_ready():
	'''
	Starts the whole application
	'''
	try:
		await command_tree.sync()
	except discord.HTTPException as e:
		print(f"Failed to sync command tree: {e}")
		logging.error("Failed to sync command tree: %s", e)

	client.loop.create_task(change_presense_periodically())
	client.loop.create_task(change_avatar_periodically())
	client.loop.create_task(give_allowance())

	await command_tree.sync(guild=discord.Object(id=int(os.getenv("DIGIMON_GUILD_ID", "0"))))  # Sync the digimon card commands to the digimon guild
	await ensure_emojis_in_guilds(client)
	
	for guild in client.guilds:
		await start_roulette_task(guild_id=guild.id)
		await start_classic_lotto_task(guild_id=guild.id)

	print("Hello, I am online!")
	print('Connected to bot: {}'.format(client.user.name))
	print('Bot ID: {}'.format(client.user.id))

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
async def on_user_update(before:discord.User, after:discord.User):
	if before.id in ignore_these_user_msgs:
		return
	if (before.avatar != after.avatar or before.display_avatar != after.display_avatar) and before.id != client.user.id:
		channel = after.mutual_guilds[0].system_channel
		if channel:
			await channel.send(pickRandomAvatarCompliment(after.mention))
		else:
			logging.error("Mutual Channel not found")
			print(f"Mutual Channel not found")

@client.event
async def on_member_update(before:discord.Member, after:discord.Member):
	if before.id in ignore_these_user_msgs:
		return
	if before.avatar != after.avatar or before.display_avatar != after.display_avatar:
		channel = after.guild.system_channel
		if channel:
			await channel.send(pickRandomAvatarCompliment(after.mention))
		else:
			logging.error("Mutual Channel not found")
			print(f"Mutual Channel not found")

@client.event
async def on_message(message:discord.Message):
	if message.author == client.user or message.author.id in ignore_these_user_msgs:
		return
	
	urls = extractor.find_urls(message.content)
	if "69" in message.content:
		skip_nice = False
		for mention in message.mentions:
			if "69" in str(mention.id):
				skip_nice = True
		for url in urls:
			if "69" in url:
				skip_nice = True
		if not skip_nice:
			database.incriment_bot_usage(guild_id=message.guild.id, user_id=message.author.id)
			await message.reply(pickRandomNiceResponse())

	if "420" in message.content:
		skip_forweed = False
		for mention in message.mentions:
			if "420" in str(mention.id):
				skip_forweed = True
		for url in urls:
			if "420" in url:
				skip_forweed = True
		if not skip_forweed:
			database.incriment_bot_usage(guild_id=message.guild.id, user_id=message.author.id)
			await message.reply(pickRandomWeedResponse())

	if client.user in message.mentions:
		database.incriment_bot_usage(guild_id=message.guild.id, user_id=message.author.id)
		await message.channel.send(pickRandomBotMentionResponse(username=message.author.mention, fail_msg="I broke myself trying to respond to you."))
	
	if "http" in message.content and "myanimelist" in message.content:
		database.incriment_bot_usage(guild_id=message.guild.id, user_id=message.author.id)
		# example https://myanimelist.net/anime/205/Samurai_Champloo or https://myanimelist.net/anime/205
		anime_id = await get_anime_id(mal_url=message.content)
		if anime_id is None:
			return
		mal_response = await mal_connection.get_anime_details(anime_id=anime_id)
		await message.channel.send(detail_MAL_Anime_Response(mal_response=mal_response, username=message.author.mention))

	if isinstance(message.channel, discord.DMChannel) and message.author.id in [390043861302509568, 259431114286956544]:  # Check if the message is a DM to the bot from megan
		# This is a private message (DM) to the bot
		await tyler_bot.add_message(role="user", content=message.content)
		response = await tyler_bot.get_msg_response()
		await message.channel.send(response)
		return

@client.event
async def on_reaction_add(reaction:discord.Reaction, user:discord.User):
	if user == client.user or user.id in ignore_these_user_reactions:
		return
	reaction_message = reaction.message
	if reaction_message.author.id in ignore_these_user_msgs:
		return

	react_roll = random.randint(1, 100)
	print(f"Reaction added by user: {user.name}. Rolled: {react_roll}")
	if react_roll >= 75:
		try:
			database.incriment_bot_usage(guild_id=reaction.message.guild.id, user_id=user.id)
			emoji_name = reaction.emoji.name if isinstance(reaction.emoji, discord.Emoji) else str(reaction.emoji)
			emoji_name_to_add = await get_bot_equivilant_emoji(emoji_name=emoji_name)
			if "bot" in emoji_name_to_add:
				emoji_to_add = await get_guild_emoji(guild=reaction_message.guild, emoji_name=emoji_name_to_add)
				await reaction_message.add_reaction(emoji_to_add)
				print(f"Added reaction: {emoji_to_add.name} to message by user: {reaction_message.author.name}")
				return
			elif "bot_" not in emoji_name_to_add and os.getenv("enable_non_bot_reactions", "false").lower() == "true":
				await reaction_message.add_reaction(reaction.emoji)
				print(f"Added reaction: {reaction.emoji} to message by user: {reaction_message.author.name}")
				return


			print(f"Did not add reaction: {reaction.emoji} to message by user: {reaction_message.author.name}")

		except Exception as e:
			logging.error(f"Failed to add reaction: {e}")
	return


#
# General Commands
#

@command_tree.command(name="roll",description="Roll a die. XdY + Z")
async def roll(interaction: discord.Interaction, dice:str, name:str=None):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=dieRoll(username=username, dice=dice, name=name) )

@command_tree.command(name="yell",description="Yell something. At someone if you like.")
async def yell(interaction: discord.Interaction, member:discord.Member=None):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	
	username = interaction.user.mention
	if member is None:
		target_username = username
	else:
		target_username = member.mention

	if member is not None and random.randint(1, 100) >= 70:
		await interaction.response.send_message(content=pickRandomNotYell(username=username))
		return
	
	if member is not None and random.randint(1, 100) >= 95:
		rand_member = get_random_guild_member(interaction.guild)
		if rand_member is None:
			print("No members found in the guild.")
		else:
			target_username = rand_member.mention

	await interaction.response.send_message(content=pickRandomYell(username=target_username))



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

@command_tree.command(name="random_selection",description="give the bot a list of options seperated by commas, and it will pick one at random.")
async def random_selection(interaction: discord.Interaction, options:str):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	if options.strip() == "":
		await interaction.response.send_message(content=f"{username}, you need to give me some options to choose from.")
		return
	
	options_list = [option.strip() for option in options.split(",")]
	if len(options_list) == 0:
		await interaction.response.send_message(content=f"{username}, you need to give me some options to choose from.")
		return
	
	selected_option = random.choice(options_list)
	await interaction.response.send_message(content=f"Options: {str(options_list)}\n\n{pickRandomSelectionResponse(username=username, choice=selected_option)}")

async def ensure_emojis_in_guilds(client: discord.Client):
	"""
	Ensures all custom emojis in emoji_data are present in every guild the client is in.
	emoji_data should be a dict: {emoji_name: emoji_image_bytes}
	"""
	bot_emojis= utility.load_config("emojis")['emoji_list'] # {name, path}
	for guild in client.guilds:
		existing_emojis = {e.name for e in guild.emojis} # list of existing emoji names in the guild
		for bot_emoji in bot_emojis:
			emoji_bytes = await get_image(path=bot_emoji['path'])
			emoji_name = f"bot_{bot_emoji['name']}"
			if emoji_name not in existing_emojis:
				try:					
					await guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
					print(f"Created emoji '{emoji_name}' in guild '{guild.name}'")
				except Exception as e:
					print(f"Failed to create emoji '{emoji_name}' in guild '{guild.name}': {e}")
					continue

@command_tree.command(name="test",description="Testing the latest code changes that imafella is working on. Don't call this.")
async def test(interaction: discord.Interaction):
	"""
	Test command to check if the bot is working.
	"""
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	interaction.response.defer()  # Deferring the response to allow for longer processing time
	

	await interaction.followup.send(content=f"{username}, this is a test command. The bot is working!")

parser = argparse.ArgumentParser(description="Run Imabot")
parser.add_argument('--test', action='store_true', help="Run Imabot in test mode using the test token")
args = parser.parse_args()

# Decide which token to use
selected_token = Test_TOKEN if args.test else TOKEN
#Runs the bot		
client.run(selected_token)