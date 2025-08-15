# Discord Banker Bot
A bot that has curreny for discord servers.

# Env File
A .env file with the following details:
DISCORD_TOKEN = Token for the bot
DISCORD_TESTING_TOKEN= Token for another bot

AVATAR_PATH = Path to where you wanna store your bot's profile pics. 
DB_PATH = Path to the .db file

ALLOWED_ADMINS= [List of integer admin ids]
ignore_user_msgs=[List of integer ignored user ids]
ignore_user_reactions=[List of integer ignored user ids]
TEST_ID = ID of the test bot
ID = ID of the main bot

mal_base_url = https://api.myanimelist.net/v2/
mal_anime_endpoint = anime/
mal_anime_fields = id,title,alternative_titles,start_date,end_date,synopsis,mean,nsfw,media_type,status,genres,num_episodes,source
mal_oauth_url = https://myanimelist.net/v1/oauth2/authorize
mal_oauth_client_id = 
mal_oauth_secret = 

roulette_table_path = Path to your picture of a roulette table.

ALLOWANCE_DAY = 5

ALLOWANCE_TIME = 10

DIGIMON_GUILD_ID=ID of the digimon discord server
digimon_base_url=https://digimoncard.io/api-public/search.php?series=Digimon Card Game&desc=include a Digimon card&sort=name&sortdirection=desc

open_ai_api_key= Get your own Open API Key

tyler_bot_id = assistant Id of your own tyler_bot.

# Modules
Bank
Roulette
Lotto
Card