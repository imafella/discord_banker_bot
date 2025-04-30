import random

def roll(max:int=10):
	return random.randint(0,max)

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