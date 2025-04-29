import datetime

def scheduleEvent(happening):
	things = happening.split(" ")
	if(len(things)<4):
		return "Error with your input, need to be: YYYY-MM-DD Time 'Event Name' format"
	else:
		date = things[0]
		time = things[1]
		name = things[2:]
