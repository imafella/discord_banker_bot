import requests
import json
import sys

def searchInput(value, url):
	searchResult = search(value, url)
	length = len(searchResult.json())
	print("Results is:"+str(length))
	if(length < 1):
		return "Sorry, nothing matching that card/name in the database"
	elif(length > 1):
		return tooManyOptions(searchResult)
	else:
		if('error' in searchResult.json()):
			return "Sorry, nothing matching that card/name in the database"
		return prettyUpSingleCard(searchResult)


def search(value, url):
	
	api = url
	#Do Card search first. card card numer & n for name
	response = requests.get(str(api)+'&card='+value)
	lenth = len(response.json())

	if(not('error' in response.json()) and (lenth)==1):
		return response
	else:
		api = url
		response = requests.get(str(api)+'&n='+value)
		return response


		

def testSearch(value, url):
	api = url
	#Do Card search first. card card numer & n for name
	response = requests.get(api+'&n='+value)
	load = json.loads(response.text)
	print("Length of results is:"+str(len(load)))
	print("Card is here:\n"+response.text)
	print("The color is:"+response.json()[0]['color'])
	return response.text

def prettyUpSingleCard(cardDetails):
	if('image_url' in cardDetails.json()[0]):
		return cardDetails.json()[0]['image_url']
	else:
		return "No image for card, here is the text:\n"+cardDetails.text

def tooManyOptions(cards):
	output = "Multiple cards have that in their name:"
	for card in cards.json():
		output+= "\n"+card['name']+":"+card['color']+":"+card['cardnumber']
	return output


def main(arg):
	print('\n'+searchInput(arg))

if __name__ == "__main__":
	main(sys.argv[1])