import random

def rollD10():
	return random.randint(0,3)

def pickGreeting(username):
	number = rollD10()
	switcher={
		0: "Welcome to the server "+username+"!",
		1:"Howdy do "+username+"!",
		2:username+" is now in the house!",
		3:"Woop woop, "+username+" is now here!",
	}
	return switcher.get(number, "I broke myself trying to say hi.")