import random

def tblFlip():
	table = random.randint(1,5)
	if (table == 1 or table == 2):
		return "(╯°□°)╯︵ ┻━┻"
	if (table == 3 or table == 4):
		return "┻━┻ ︵╰(°□°╰)"
	if (table == 5):
		return "┻━┻ ︵╰(°□°)╯︵ ┻━┻"