import random
from ThingyDo import utility

avatar_compliment_config = utility.load_config("AvatarCompliments")
goodbot_replies_config = utility.load_config("GoodBotReplies")
tsudre_replies_config = utility.load_config("TsundreMentions")
crit_replies_config = utility.load_config("MaxRollResponses")

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

def pickRandomResponse(username:str, config:dict, fail_msg:str = "I broke myself trying to respond to you."):
	total = len(config)
	number = roll(total)
	return pickResponse(username, config, number, fail_msg)

def pickResponse(username:str, config:dict, number:int = 1, fail_msg:str = "I broke myself trying to respond to you."):
	# Pick a random compliment from the list
	total = len(config)
	if number > total:
		number = total
	return f"{username}, {config.get(str(number), fail_msg)}"

def giveInfo():
	output= "Hello,\nImabot. I do things that imafella and other discord users tells me to. Please don't talk to me."
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