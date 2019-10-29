import requests
import hashlib
import time
from tkinter import *
import json
import random

def sendMarvelRequest(request):
	'stuurt een aanvraag naar de Marvel API'
	loginInfo=json.load(open('apikey.json','r'))
	stamp=str(time.time())
	pubkey=loginInfo['pubkey']
	privatekey=loginInfo['privatekey']
	hashString=stamp+privatekey+pubkey
	hash=hashlib.md5(hashString.encode()).hexdigest()
	httprequest=requests.get(f'https://gateway.marvel.com/v1/public/{request}&ts={stamp}&apikey={pubkey}&hash={hash}')
	return json.loads(httprequest.text)['data']['results']

def selectCharacter():
	while True:
		randomNumber=random.randint(0,1400)
		characters=sendMarvelRequest(f'characters?offset={randomNumber}')
		for character in characters:
			if len(character['description'])>0:
				return character,characters
def selectNames(characters,exclude):
	names=[exclude]
	while len(names)<4:
		character=random.choice(characters)
		if character['name'] not in names:
			names.append(character['name'])
	return names
		
#print(json.dumps(sendMarvelRequest('characters'), sort_keys=True,indent=4, separators=(',', ': ')))
character,characters=selectCharacter()
name=character['name']
names=selectNames(characters,name)
description=character['description'].replace(name,'<naam>')
print(names)
print(description)
print(name)
