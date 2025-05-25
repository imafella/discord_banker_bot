import random
from ThingyDo import utility

avatar_compliment_config = utility.load_config("AvatarCompliments")
goodbot_replies_config = utility.load_config("GoodBotReplies")
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

def pickRandomCritResponse(username:str=None):
	return pickRandomResponse(username=username,config=crit_replies_config, fail_msg="Your crit broke me.")

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

def pickRandomYell(username:str=None):
	config = utility.load_config("yelling")['yelling']
	# Pick a random yell from the list
	output = pickRandomResponse(config=config, fail_msg="I broke myself trying to yell.")
	if '[member]' not in output and username is not None:
		return f"{username}, {output}"
	elif '[member]' in output and username is not None:
		return output.replace('[member]', username)
	elif '[member]' in output and username is None:
		return f"{output.replace('[member]', "Valued User")}"
	else: 
		# '[member]' not in output and username is None:
		return output
	
def pickRandomNotYell(username:str=None):
	config = utility.load_config("yelling")['not_yelling']
	# Pick a random yell from the list
	output = pickRandomResponse(config=config, fail_msg="I broke myself trying to yell.")
	if '[member]' not in output and username is not None:
		return f"{username}, {output}"
	elif '[member]' in output and username is not None:
		return output.replace('[member]', username)
	elif '[member]' in output and username is None:
		return f"{output.replace('[member]', "Valued User")}"
	else: 
		# '[member]' not in output and username is None:
		return output
	
def pickRandomBotMentionResponse(username:str=None, fail_msg:str="I broke myself trying to respond to you."):
	# Pick a random bot mention response from the list
	bot_mentions_config = utility.load_config("BotMentionResponses")
	output = pickRandomResponse(config=bot_mentions_config, fail_msg=fail_msg)

	if username is not None and '[member]' in output:
		return output.replace("[member]", username)
	elif username is not None and '[member]' not in output:
		return f"{username}, {output}"
	else:
		return output
	
def pickRandomAwardMoneyResponse(amount:float, guild_currency_name:str, guild_currency_symbol:str, username:str, reason:str=None):
	list = utility.load_config("StaticResponses")['bank']['award']

	if reason is None:
		list = list['without_reason']
	else:
		list = list['with_reason']
	response = pickRandomResponseNew(list = list, username = username )
	if reason is not None:
		response = response.replace('[REASON]', reason)
	
	response = replace_bank_tags(message=response, user_mention=username, currency_name=guild_currency_name, currency_symbol=guild_currency_symbol, amount=amount)
	
	return response

def pickRandomResponseNew(list:list, fail_msg:str = "I broke myself trying to respond to you.", username:str=None) -> str:
	total = len(list)
	number = roll(total)-1
	return pickResponseNew(username=username, list=list, number=number, fail_msg=fail_msg)

def pickResponseNew(list:list, number:int = 0, fail_msg:str = "I broke myself trying to respond to you.", username:str=None) -> str:
	# Pick a random compliment from the list
	total = len(list)
	if number > total:
		number = total
	try:
		if username is None:
			return f"{list[number]}"
		return f"{username}, {list[number]}"
	except:
		return fail_msg

def pickRandomResponse(config:dict, fail_msg:str = "I broke myself trying to respond to you.", username:str=None):
	total = len(config)
	number = roll(total)
	return pickResponse(username=username, config=config, number=number, fail_msg=fail_msg)

def pickResponse(config:dict, number:int = 1, fail_msg:str = "I broke myself trying to respond to you.", username:str=None):
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
	for value in utility.load_config("StaticResponses").get("commands", []):
		output+= f"{value}\n"
	return output

# def shout(username):
# 	return "I DISLIKE YOU "+str(username)



def tblFlip():
	table = random.randint(1,5)
	if (table == 1 or table == 2):
		return "(╯°□°)╯︵ ┻━┻"
	if (table == 3 or table == 4):
		return "┻━┻ ︵╰(°□°╰)"
	if (table == 5):
		return "┻━┻ ︵╰(°□°)╯︵ ┻━┻"
	
def replace_bank_tags(message:str, user_mention:str, currency_name:str, currency_symbol:str, bank_balance:float=0, name_cost:float=0, symbol_cost:float=0, amount:float=0) -> str:
	# Replace the tags in the message with the user's mention and bank balance
	
	return message.replace("[USER]", user_mention).replace("[BANK_BALANCE]", str(bank_balance)).replace("[CURRENCY_NAME]", currency_name).replace("[CURRENCY_SYMBOL]", currency_symbol).replace("[CURRENCY_NAME_CHANGE_COST]",str(name_cost)).replace("[CURRENCY_SYMBOL_CHANGE_COST]", str(symbol_cost)).replace('[AMOUNT]', str(amount))