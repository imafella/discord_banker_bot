import random
import re

def dieRoll(username, message):
	if (message == ""):
		return "You need a die to roll."
	while (message[:6] == "!roll "):
		message = message[6:]
	match = re.fullmatch("[\d]+d[\d]+", message)
	if (match):
		a = int(message[0:1])
		b = int(message[2:])
		roll = str(random.randint(a,(a*b)))
		return username + " rolled " + roll
	else:
		return username + ", that's not a valid roll call.  Usage: !roll XdX"