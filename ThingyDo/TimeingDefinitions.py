from datetime import datetime

def defineOnPlay():
	return "On Play \n\nTriggers when Digimon are played directly to the battle area. \nDoes not apply to digivolving Digimon or Digimon moved into play from the breeding \narea."

def defineWhenDigivolving():
	return "When Digivolving \n\n Triggers when a Digimon on the field digivolves. \n Digimon digivolved in the breeding \n area do not activate their When Digivolving \n effects. These effects activate after the player draws a card for the digivolution bonus."

def defineWhenAttacking():
	return "When Attacking \n\n Triggers when an attack is declared with the Digimon that has the [When Attacking] \n effect. \n Triggers at the same time as effects that read 'when one of your Digimon attacks'."

def defineEndOfAttack():
	return "End of Attack \n\n Triggers after the resolution of the attack made by any Digimon with effects with this \n timing, and any effects that attack triggers. \n If that Digimon loses the battle or leaves play during the attack, the End of Attack \n effect doesn’t activate."

def defineAtTheEndOfTheBattle():
	return "At the end of the battle \n\n During battles between Digimon or between a Digimon and a Security Digimon, 'at \n the end of the battle' timing occurs after comparing DP and determining the battle's \n outcome."

def defineReactions():
	return "Reactions \n\n When you attack with a Digimon, reaction timing occurs when all [When Attacking] \n and 'When one of your Digimon attacks' effects—along with all effects triggered by \n those effects—finish activating. \n Triggered by your opponent's effects that read 'When an opponent's Digimon \n attacks'."

def defineOnDeletion():
	return "On Deletion \n\n Triggers when a Digimon is defeated in battle, deleted by a card effect, or deleted \n when its DP is reduced to 0."

def defineYourTurn():
	return "Your Turn \n\n The period lasting from the start of your turn to its end."

def defineOpponentsTurn(): 
	return "Opponent's Turn \n\n The period lasting from the start of your opponent’s turn to its end."

def defineAllTurns(): 
	return "All Turns \n\n The period lasting from the start of your turn to the end of your opponent's turn."

def defineStartOfYourTurn(): 
	return "Start of your Turn \n\n Resolved when your turn begins."

def defineEndOfYourTurn(): 
	return "End of Your Turn \n\n Resolved when your turn ends."

def defineSecurity():
	return "Security \n\n When a card is turned over for a security check. \n If the security card that is flipped over has this kind of effect, it activates \n automatically and has no memory cost."

def defineMain():
	return "Main \n\n Effects that can be activated during your main phase. \n Applies to Option cards activated from your hand, or using optional effects of \n Digimon or Tamers during the main phase."

def pickTiming(arg):
	value = arg.lower()
	if(value in ['main']):
		return defineMain()
	elif(value in ['security', 'sec']):
		return defineSecurity()
	elif(value in ['end of your turn', 'end of turn']):
		return defineEndOfYourTurn()
	elif(value in ['start of your turn', 'start of turn']):
		return defineStartOfYourTurn()
	elif(value in ['all turns', 'all turn']):
		return defineAllTurns()
	elif(value in ['opponents turn', 'opponent turn']):
		return defineOpponentsTurn()
	elif(value in ['your turn', 'my turn']):
		return defineYourTurn()
	elif(value in ['on deletion', 'on delete']):
		return defineOnDeletion()
	elif(value in ['reaction', 'reactions']):
		return defineReactions()
	elif(value in ['at the end of battle', 'end of battle']):
		return defineAtTheEndOfTheBattle()
	elif(value in ['end of attack']):
		return defineEndOfAttack()
	elif(value in ['when attacking', 'when one of your digimon attacks']):
		return defineWhenAttacking()
	elif(value in ['on play', 'play']):
		return defineOnPlay()
	else:
		now = datetime.now()
		currentTime = now.strftime("%H:%M:%S")
		print("\n"+currentTime+"\n"+arg)
		return "Invalid timing query. Please yell at imafella about this. I hear he is a bitch."

def main():
	print('\n'+pickTiming('on'))

if __name__ == "__main__":
	main()