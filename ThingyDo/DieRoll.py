import random
import re
from ThingyDo.Messages import pickRandomCritResponse

def dieRoll(username, dice:str="1d6", name:str=None):
	if (dice == "") or dice.isalpha() or dice.isdigit():
		return "You need a die to roll my dude. \nTry using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."
	
	pattern = r"[+-]?\d*d\d+|[+-]?\d+"

	matches = re.findall(pattern, dice)
	if len(matches) == 0:
		return f"{username}, that's not a valid roll call.\nRoll:{dice} Try using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."

	modifiers = []
	modifier_total = 0
	dice_rolls = {} # 'msg':str, num_of_rolls:int, rolls:[str], total:int

	for element in matches:		
		multiplier = 1
		leading_sign = element[0]
		if leading_sign == "+" or leading_sign == "-":
			#remove the sign
			element = element[1:]
			if leading_sign == "-":
				multiplier = -1
			
		if 'd' in element: # element is a die roll:
			current_roll = {}
			rolls = []
			total = 0
			msg = ""

			dice_rolls[element] = {}

			split = element.split('d')
			if (len(split) != 2):
				current_roll['msg'] = f"{element} is not a valid roll. Try using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."
				dice_rolls[element]= current_roll
				continue
			num_of_die = split[0]
			die_to_roll = split[1]

			if (not num_of_die.isdigit() or not die_to_roll.isdigit()) or (int(die_to_roll) < 1):
				current_roll[msg] = f"{element} is not a valid roll. Try using the format XdY, where X is the number of dice and Y is the number of sides on the die.\nExample: 1d6, 2d20, 3d8, etc."
				dice_rolls[element] = current_roll
				continue
			num_of_die = int(num_of_die)
			die_to_roll = int(die_to_roll)

			current_roll['num_of_rolls'] = num_of_die

			if num_of_die > 999:
				current_roll['msg'] = f"I don't own {num_of_die} d{die_to_roll}'s"
				dice_rolls[element] = current_roll
				continue
			
			for i in range(num_of_die):
				roll = random.randint(1, die_to_roll)
				rolls.append(f"{roll}")
				total += roll

			if num_of_die > 20:
				current_roll['rolls'] = ["Way too many rolls to show. Trust me."]
			else:
				current_roll['rolls'] = rolls
			current_roll['total'] = total*multiplier

			
			if total == num_of_die * die_to_roll * multiplier:
				msg += f" {pickRandomCritResponse()}\n"
			
			current_roll['msg'] = msg

			# TODO handle multiples of the same element 
			# if element in dice_rolls
			dice_rolls[element] = current_roll
		else: # element is a modifier
			if element.isdigit():
				modifier_total += multiplier * int(element)
				if leading_sign != "-":
					leading_sign = "+"
				modifiers.append(f"{leading_sign}{element}")
			else:
				continue
	
	output = f"{username} rolled: {dice}"
	if name is not None:
		output+= f" for a {name} roll"
		output+="\n"
	output += "```"

	# Table header    
	output += f"{'Roll':<10} {'Results':<45} {'Total':<10} {'Msg':<25}\n"
	output += "=" * 70 + "\n"

	grand_total = 0
	# Dice Rolls
	for key in dice_rolls.keys():
		rolls = ', '.join(dice_rolls.get(key, {}).get('rolls',[]))
		total = dice_rolls.get(key, {}).get('total',0)
		msg = dice_rolls.get(key, {}).get('msg',"")

		if msg != "" and 'rolls' not in dice_rolls.get(key, {}):
			rolls = msg
			msg = ""


		output += f"{key:<10} {rolls:<45} {"["+str(total)+"]":<10} {msg:<25}\n"
		grand_total+=int(total)

	# Modifiers
	if modifier_total != 0:
		output += "=" * 70 + "\n"
		output += f"{'Modifiers:':<10} {' '.join(modifiers):<45} {"["+str(modifier_total)+"]":<10}\n"
		grand_total+=modifier_total

	# Grand Total
	output += "=" * 70 + "\n"
	output += f"{'Grand Total:':<10} {grand_total}\n"
	output += "```"  # End code block

	return output
	