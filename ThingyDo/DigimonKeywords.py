def getBlocker():
	return "<Blocker> \n When an opponent's Digimon attacks, you may suspend this Digimon to force the opponent to attack it instead. This effect can be used against an attack from an opposing Digimon. The target of the attack changes to the Digimon that used <Blocker>, taking the place of the original target. The timing of blocker is after all when attacking triggers are finished."

def getSecAttackPlus():
	return "<Security Attack +> \nThis Digimon checks x additional security card(s). Effect that increases the number of security cards checked by x when attacking the opposing player. When checking multiple security cards due to this effect, do not flip all security cards over at once. Instead, flip them over one at a time and don’t move on to the next one until everything has resolved. If the attacking Digimon is defeated in battle or returned to the player’s hand, the attack ends."

def getSecAttackMinus():
	return "<Security Attack -> \nThis Digimon checks x fewer security card(s). Effect that decreases the number of security cards checked by x when attacking the opposing player. If this effect causes the number of cards checked to become zero (it can’t be less than zero), the opponent’s security cards aren’t checked. If your opponent has zero security cards and you attack with a Digimon that checks zero cards, you can’t win the game."

def getRecovery():
	return "<Recovery x> \nPlace the top x card(s) of your deck on top of your security stack. Effect that has you to place x cards from your deck on top of your security stack without looking at them. With this effect, you can replenish your security stack. There is no limit to how many cards can be in your security stack."

def getPiercing():
	return "<Piercing> \nWhen this Digimon attacks and deletes an opponent's Digimon and survives the battle, it performs any security checks it normally would. This effect allows a Digimon to check an opponent’s security cards after a battle if your Digimon defeats the opposing Digimon and survives. This effect also works if an attack is blocked, however it does not activate for battles with Security Digimon. Security checks resulting from <Piercing> are performed after all effects resulting from the battle have been resolved."

def getDraw():
	return "<Draw x> \nDraw x card(s) from your deck.\n This effect allows you to add a number of cards to your hand from your deck. There\n  is no limit to how many cards you can have in your hand."

def getJamming():
	return "<Jamming> \nThis Digimon can't be deleted in battles against Security Digimon. \n Digimon with this effect will not be deleted if they lose a battle with the opponent’s \n Security Digimon. If the Digimon has a Security Attack + effect that allows for an \n additional security card to be checked, that check can still be performed"

def getDigisorption():
	return "<Digisorption x> \nWhen one of your Digimon digivolves into this card from your hand, you may \n suspend of your 1 Digimon to reduce the memory cost of the digivolution by x. \n When digivolving into a card in your hand with this effect, you may suspend 1 of \n your Digimon to reduce the digivolve cost by the number specified in the effect. \n However, the digivolve cost can’t be reduced to less than zero."

def getReboot():
	return "<Reboot> \nUnsuspend this Digimon during your opponent's unsuspend phase. \n Digimon with this effect are unsuspended during not only your unsuspend phase, \n but your opponent’s unsuspend phase as well."

def getDeDigivolve():
	return "<De-Digivolve x> \nTrash up to x cards from the top of one of your opponent's Digimon. If it has no \n digivolution cards, or becomes a level 3 Digimon, you can't trash any more cards. \n Trash the number of cards specified from your opponent’s Digimon that was \n targeted by the effect, starting from the top. This reduces the level of the target \n Digimon. However, Digimon can’t be deleted or removed from play with this effect. \n Once a Digimon has lost all of its digivolution cards or has been reduced to level 3, \n you can’t trash any more cards with this effect."

def getRetaliation():
	return "<Retaliation> \nWhen this Digimon is deleted after losing a battle, delete the Digimon it was battling. \n When a Digimon with this effect loses a battle with one of your opponent’s Digimon, \n it deletes that Digimon, regardless of DP."

def getDigiburst():
	return "<Digi-Burst x> \nTrash X of this Digimon's digivolution cards to activate the effect below. \n A Digimon with this effect has a <Digi-Burst> effect you can activate by trashing the \n specified number of digivolution cards from it at the specified timing."

def getRush():
	return "<Rush> \nThis Digimon can attack the turn it comes into play. \n Digimon with this effect can ignore the rule that states 'Digimon can't attack the turn \n they enter play' and attack as soon as they're played."

def getBlitz():
	return "<Blitz> \nThis Digimon can attack when your opponent has 1 or more memory. \n When digivolving into a Digimon with this effect, you can attack with it before the turn \n ends even if paying the digivolution cost moved the memory gauge to 1 or more on \n the opponent's side. \n However, if the Digimon is suspended, has an effect that prevents it from attacking, \n or is otherwise unable to attack normally, <Blitz> won't enable it to attack."

def getDelay():
	return "<Delay> \nTrash this card in your battle area to activate the effect below. You can't activate this \n effect the turn this card enters play. \n After placing an Option card with this effect in your battle area, you can trash it at the \n timing specified to activate the card's <Delay> effect. \n It's not necessary to pay an Option card's memory cost or meet color requirements \n when activating its <Delay> effect."

def getDecoy():
	return "<Decoy (X)> \nWhen one of your other (X) Digimon would be deleted by an opponent's effect, you \n may delete this Digimon to prevent that deletion. \n When one of your (X) Digimon would be deleted by an opponent's 'delete' effect, \n you can delete the Digimon with this effect instead to prevent the other Digimon from \n being deleted. When multiple applicable Digimon are deleted simultaneously, you \n can only use this effect to prevent one of them from being deleted. \n If the Digimon with this effect is deleted, you can't activate this effect."

def getArmorPurge():
	return "<Armor Purge> \nWhen this Digimon would be deleted, you may trash the top card of this Digimon to \n prevent that deletion. \n When one of your Digimon with this effect would be deleted, this effect allows you to \n trash the top card of that Digimon to prevent it from being deleted. The Digimon that \n activates this effect then becomes the top Digimon in its digivolution cards. Digimon \n with no digivolution cards can't activate this effect. \n Additionally, any effects that are affecting the Digimon prior to activating <Armor \n Purge> carry over. (Other than effects that are lost as a result of trashing cards.)"