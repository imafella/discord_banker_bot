import random
from ThingyDo import utility

avatar_compliment_config = utility.load_config("AvatarCompliments")
goodbot_replies_config = utility.load_config("GoodBotReplies")
tsudre_replies_config = utility.load_config("TsundreMentions")
crit_replies_config = utility.load_config("MaxRollResponses")
bank_messages_config = utility.load_config("bank_messages")
activities_config = utility.load_config("Activities")

def roll(max:int=10):
	return random.randint(1,max)

def pickGreeting(username):
	number = roll()
	welcome_message={
		0: "Welcome to the server "+username+"!",
		1:"Howdy do "+username+"!",
		2:username+" is now in the house!",
		3:"Woop woop, "+username+" is now here!",
		4:"Hello "+username+"!",
		5:"Greetings "+username+"!",
		6:"Salutations "+username+"!",
		7:"Hiya "+username+"!",
		8:"Hey "+username+"!",
		9:"Yo "+username+"!",
		10:"Sup "+username+"!"
	}
	return f"{welcome_message.get(number, 'I broke myself trying to say hi.')} Thanks for joining the server!"

####
# Pick Random Responses
###
def pickRandomAvatarCompliment(username):
	# Pick a random compliment from the list
	return pickRandomResponse(username=username,config=avatar_compliment_config,fail_msg="I broke myself trying to compliment you.")
	
def pickRandomGoodBotResponse(username):
    # Pick a random bashful comment from the list
	return pickRandomResponse(username=username,config=goodbot_replies_config,fail_msg="I broke myself trying to respond to you.")

def pickRandomTsundreResponse(username):
    # Pick a random Tsundere comment from the list
	return pickRandomResponse(username=username, config=tsudre_replies_config, fail_msg="I broke myself trying to respond to you.")

def pickRandomCritResponse(username):
	return pickRandomResponse(username=username, config=crit_replies_config, fail_msg="Your crit broke me.")

def pickRandomBankWelcomeResponse(username:str, currency_name:str, currency_symbol:str, bank_balance:float):
	response = pickRandomResponse(username=None, config=bank_messages_config["welcome_to_bank"], fail_msg="I broke myself trying to help you join the bank.")
	return replace_bank_tags(message=response, user_mention=username, bank_balance=bank_balance, currency_name=currency_name, currency_symbol=currency_symbol)

def pickRandomYouAlreadyHaveAnAccountResponse(username:str, currency_name:str, currency_symbol:str, bank_balance:float):
	response = pickRandomResponse(username=None, config=bank_messages_config["already_have_account"], fail_msg="I broke myself.")
	return replace_bank_tags(message=response, user_mention=username, bank_balance=bank_balance, currency_name=currency_name, currency_symbol=currency_symbol)

def pickRandomYouDontHaveAnAccountResponse(username:str, currency_name:str, currency_symbol:str):
	response = pickRandomResponse(username=None, config=bank_messages_config["doesnt_have_account"], fail_msg="I broke myself.")
	return replace_bank_tags(message=response, user_mention=username, bank_balance=0, currency_name=currency_name, currency_symbol=currency_symbol)

def pickRandomLeavingTheBankResponse(username:str, currency_name:str, currency_symbol:str, bank_balance:float):
	response = pickRandomResponse(username=None, config=bank_messages_config["leaving_bank"], fail_msg="I broke myself kicking you out of the bank.")
	return replace_bank_tags(message=response, user_mention=username, bank_balance=bank_balance, currency_name=currency_name, currency_symbol=currency_symbol)

def pickRandomBankBalanceResponse(username:str, bank_balance:float, currency_name:str, currency_symbol:str):
	# Pick a random bank balance response from the list
	response = pickRandomResponse(username=None, config=bank_messages_config["balance_messages"], fail_msg="I broke myself trying to help you with your bank balance.")
	return replace_bank_tags(message=response, user_mention=username, bank_balance=bank_balance, currency_name=currency_name, currency_symbol=currency_symbol)

def pickRandomChangeCostResponse(username:str, currency_name:str, currency_symbol:str, name_cost:float, symbol_cost:float):
	# Pick a random bank balance response from the list
	response = pickRandomResponse(username=None, config=bank_messages_config["change_cost_messages"], fail_msg="I broke myself trying to help you with your costs.")
	return replace_bank_tags(message=response, user_mention=username, currency_name=currency_name, currency_symbol=currency_symbol, name_cost=name_cost, symbol_cost=symbol_cost)

def pickRandomActivity():
	# Pick a random activity response from the list
	return pickRandomResponse(username=None, config=activities_config, fail_msg="I broke myself trying to pick an activity.")

def pickRandomResponse(username:str, config:dict, fail_msg:str = "I broke myself trying to respond to you."):
	total = len(config)
	number = roll(total)
	return pickResponse(username, config, number, fail_msg)

def pickResponse(username:str, config:dict, number:int = 1, fail_msg:str = "I broke myself trying to respond to you."):
	# Pick a random compliment from the list
	total = len(config)
	if number > total:
		number = total
	if username is None:
		return f"{config.get(str(number), fail_msg)}"
	return f"{username}, {config.get(str(number), fail_msg)}"

def giveInfo():
	output= "Hello,\nImabot. I do things that imafella and other discord users tells me to. Please don't talk to me.\n\n"
	output+= "I can do the following things:\n\n"
	output+= "roll - Roll a die. XdY + Z\nyell - Yell something.\ntest - this is for testing. Leave it alone.\nflip - Flips the table\ninfo - Info about the bot.\ngood_bot - Tell the bot it's a good bot.\njoin_bank - Make a bank account. Join the server bank. One of us.\nbank_balance - Get your bank balance.\nleave_bank - Close your bank account.\nget_change_costs - Get the costs of changing the currency name and symbol.\nchange_currency_name - Change the currency name.\nchange_currency_symbol - Change the currency symbol.\ntransfer_money - Transfer money to another user.\naward - Award money to a user.\nset_bank_balance - Set the bank balance of a user.\nget_currency_details - Get the currency details."
	return output

def shout(username):
	return "I DISLIKE YOU "+str(username)

def tblFlip():
	table = random.randint(1,5)
	if (table == 1 or table == 2):
		return "(╯°□°)╯︵ ┻━┻"
	if (table == 3 or table == 4):
		return "┻━┻ ︵╰(°□°╰)"
	if (table == 5):
		return "┻━┻ ︵╰(°□°)╯︵ ┻━┻"
	
def replace_bank_tags(message:str, user_mention:str, currency_name:str, currency_symbol:str, bank_balance:float=0, name_cost:float=0, symbol_cost:float=0) -> str:
	# Replace the tags in the message with the user's mention and bank balance
	
	return message.replace("[USER]", user_mention).replace("[BANK_BALANCE]", str(bank_balance)).replace("[CURRENCY_NAME]", currency_name).replace("[CURRENCY_SYMBOL]", currency_symbol).replace("[CURRENCY_NAME_CHANGE_COST]",str(name_cost)).replace("[CURRENCY_SYMBOL_CHANGE_COST]", str(symbol_cost))