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
	'selecteert een character die een beschrijving heeft'
	while True:
		randomNumber=random.randint(0,1400)
		characters=sendMarvelRequest(f'characters?offset={randomNumber}')
		for character in characters:
			if len(character['description'])>0:
				return character,characters

def selectNames(characters,exclude):
	'selecteert de namen die gebruikt worden bij multiplechoice'
	names=[exclude]
	while len(names)<4:
		character=random.choice(characters)
		if character['name'] not in names:
			names.append(character['name'])
	return names

def guiData():
	character,characters=selectCharacter()
	name=character['name']
	names=selectNames(characters,name)
	description=character['description'].replace(name,'<naam>')
	return names,description,name
#print(guiData())


# Tkinter GUI
root = Tk()

canvas = Frame(root, width=700, height=700)
welcomeMessage = Label(root, text="Welkom bij de Marvel Quiz!")
nameLabel = Label(root, text="Naam:")
nameEntry = Entry(root)

canvas.pack()
nameLabel.grid(row=0, sticky=E)
nameEntry.grid(row=0, column=1)



root.mainloop()