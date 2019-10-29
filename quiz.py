import requests
import hashlib
import time
from tkinter import *
import json
import random
import threading
characterBuffer=[]
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
		characters=sendMarvelRequest(f'characters?offset={randomNumber}&orderBy=modified')
		for character in characters:
			if len(character['description'])>0:
				return character,characters

def selectNames(characters,exclude):
	'selecteert de namen die gebruikt worden bij multiplechoice'
	names=[exclude]
	while len(names)<10:
		character=random.choice(characters)
		if character['name'] not in names:
			names.append(character['name'])
	return names

def guiData():
	character,characters=selectCharacter()
	name=character['name']
	names=selectNames(characters,name)
	description=character['description'].replace(name,'<naam>')
	return {'names':names,'description':description,'name':name}
#print(guiData())
def buffer_character():
	characterBuffer.append(guiData())
def start_buffer_thread():
	api_thread = threading.Thread(target=buffer_character)
	api_thread.start()

def get_new_character():
	start_buffer_thread()
	return characterBuffer.pop()

def init_buffer():
	start_buffer_thread()
	start_buffer_thread()

#init_buffer()
#time.sleep(5)
#print(get_new_character(),characterBuffer)

# Tkinter GUI
root = Tk()
# Main frame settings
root.resizable(width=False, height=False)
root.geometry('1280x720')

nameLabel = Label(root, text="Naam:")
nameEntry = Entry(root)

nameLabel.grid(row=0, sticky=E)
nameEntry.grid(row=0, column=1)

root.mainloop()