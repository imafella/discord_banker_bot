import random
import re
from ThingyDo.Messages import pickRandomCritResponse

def dieRoll(username, dice:str="1d6", modifier:int=0):
	if (dice == "") or dice.isalpha():
		return "You need a die to roll my dude. \nTry using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."
	
	mod_str = ""
	if (modifier != 0):
		mod_str = f" Modifier: {modifier}"
	
	match = re.fullmatch("([\d]+d[\d]+){1}(\+?([\d]+d[\d]+){1})*", dice)
	if (match):
		
		sum = 0
		different_rolls = dice.split("+")
		roll_string = "\nRoll Total:"
		if (len(different_rolls) > 1):
			roll_string += "\n"
		for roll in different_rolls:
			split = dice.split("d")
			if (len(split) != 2):
				return f"{username}, that's not a valid roll call.\nRoll:{dice}{mod_str}\n Try using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."
		
			a = split[0]
			b = split[1]

			if (not a.isdigit() or not b.isdigit()) or (int(b) < 1):
				return f"{username}, that's not a valid roll call.\nRoll:{dice}{mod_str}\nTry using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."

			a = int(a)
			b = int(b)

			rolls = []
			rolls_sum=0
			if a > 999:
				return username + f", I don't own {a} d{b}'s "
			for i in range(a):			
				roll = random.randint(1,b)
				rolls.append(roll)
				rolls_sum += roll
		
		
			#So many rolls...
			crit_msg = ""
			#If that was a crit, add a response
			if sum == b:
				crit_msg = f" {pickRandomCritResponse(username)}"
			if a > 100:
				roll_string += f" [Too many rolls to show all]({rolls_sum}){crit_msg}\n"
			elif a == 1:
				roll_string += f" {rolls_sum}{crit_msg}\n"
			else:
				roll_string += f" {str(rolls)}({rolls_sum}){crit_msg}\n"

			
			sum += rolls_sum
			

		if modifier == 0:
			return f"{username} rolled: {dice}{roll_string}"
		return f"{username} rolled: {dice}+{modifier}{roll_string}\nGrand Total: {sum+modifier}"
	else:
		return f"{username}, that's not a valid roll.\nRoll:{dice}{mod_str}\nTry using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."