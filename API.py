try:
	from PIL import Image, ImageTk
except:
	showinfo("ERROR","pillow is niet (correct) geinstalleerd.")
	exit()
import hashlib
import time
import json
import random
import urllib.request
import urllib.parse
import re
import io
questionBuffer = []
def sendMarvelRequest(request):
	'stuurt een aanvraag naar de Marvel API'
	loginInfo = json.load(open('apikey.json', 'r'))
	stamp = str(time.time())
	pubkey = loginInfo['pubkey']
	privatekey = loginInfo['privatekey']
	hashString = stamp + privatekey + pubkey
	hash = hashlib.md5(hashString.encode()).hexdigest()
	jsondata=urllib.request.urlopen(f'https://gateway.marvel.com/v1/public/{request}&ts={stamp}&apikey={pubkey}&hash={hash}').read()
	return json.loads(jsondata)['data']['results']

def selectCharacter():
	'selecteert een willekeurig character die een beschrijving heeft'
	while True:
		randomNumber = random.randint(0, 1400)
		characters = sendMarvelRequest(f'characters?offset={randomNumber}&orderBy=modified')

		for character in characters:
			if (len(character['description']) > 0) and (len(character['description']) < 200) and (character['thumbnail']['path']!="http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available") and (character['thumbnail']['extension']=='jpg'):
				return character, characters

def selectNames(characters, exclude):
	'selecteert de namen die gebruikt worden bij multiplechoice'
	names = [exclude]
	while len(names) < 10:
		character = random.choice(characters)
		if character['name'] not in names:
			names.append(character['name'])
	random.shuffle(names)
	return names

def questionInfo():
	'geeft de informatie die nodig is per vraag'
	character, characters = selectCharacter()
	name = character['name']
	beschrijving = character['description']
	names = selectNames(characters, name)
	replace_regex = re.compile(re.escape(name), re.IGNORECASE)  # zoeken zonder op hoofdletters te letten.
	description = replace_regex.sub('<naam>', character['description'])
	urlpath = character['thumbnail']['path']
	urlextension = character['thumbnail']['extension']
	url = f"{urlpath}/portrait_uncanny.{urlextension}"
	raw_data = urllib.request.urlopen(url).read()
	img = ImageTk.PhotoImage(Image.open(io.BytesIO(raw_data)))
	return {'names': names, 'description': description, 'name': name, 'img':img}
def bufferVraag():
	'zet de nieuwe vraag in de buffer.'
	try:
		questionBuffer.append(questionInfo())
	except:
		time.sleep(3)
		bufferVraag()
def getQuestion():
	if len(questionBuffer)>0:
		return questionBuffer.pop()
	else:
		showinfo("Error", "Het downloaden van de vragen is niet gelukt.\nKlik op OK om het opnieuw te proberen.")
		return getQuestion()