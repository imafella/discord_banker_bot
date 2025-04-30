import random
import re

def dieRoll(username, dice:str="1d6", modifier=0):
	if (dice == ""):
		return "You need a die to roll."
	match = re.fullmatch("[\d]+d[\d]+", dice)
	if (match):
		split = dice.split("d")
		if (len(split) != 2):
			return f"{username}, that's not a valid roll call.\nRoll:{dice} Modifier:{modifier}"
		a = int(split[0])
		b = int(split[1])
		rolls = []
		sum=0
		if a > 999:
			return username + ", I don't own that many dice."
		for i in range(a):			
			roll = random.randint(1,b)
			rolls.append(roll)
			sum += roll
		roll_string = ""
		if len(rolls) == 1 or len(rolls) > 100:
			roll_string = f"\nRoll Total: {sum}"
		else:
			roll_string = f"\nRolls: {str(rolls)}({sum})"
		return f"{username} rolled: {dice}+{modifier}{roll_string}\nGrand Total: {sum+modifier}"
	else:
		return f"{username}, that's not a valid roll.\nRoll:{dice} Modifier:{modifier}"