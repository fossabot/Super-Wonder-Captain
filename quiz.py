import requests
import hashlib
import time
from tkinter import *
import json
import random
import threading
import re
import sqlite3
import math

connection=sqlite3.connect('quiz.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS `scores` (`name` TEXT,`timestamp` INT(10),`score` INT(3));')
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
	random.shuffle(names)
	return names

def guiData():
	character,characters=selectCharacter()
	name=character['name']
	names=selectNames(characters,name)
	replace_regex = re.compile(re.escape(name), re.IGNORECASE)#zoeken zonder op hoofdletters te letten.
	description=replace_regex.sub('<naam>', character['description'])
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
	time.sleep(2)

init_buffer()
#time.sleep(5)
print(get_new_character(), characterBuffer)
def displayCharacter():
	character=get_new_character()

def einde_spel(naam,score):
	timestamp=math.floor(time.time())
	cursor.execute('INSERT INTO scores(name, timestamp, score) VALUES (?,?,?);', (naam,timestamp,score))
	connection.commit()

def highscores():
	cursor.execute('SELECT * FROM scores ORDER BY scores.score DESC LIMIT 10;')
	data=cursor.fetchall()
	return data
#print(highscores())
#init_buffer()
#time.sleep(3)


# Tkinter GUI
root = Tk()

# Main frame settings
root.resizable(width=False, height=False)
root.geometry('1280x800')
background_image = PhotoImage(file="marvel-login-screen.png")
background_label = Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

leftMiddleFrame = Frame(root)
leftMiddleFrame.pack(side=LEFT, anchor=W, padx=(45, 0))

nameLabel = Label(leftMiddleFrame, text="Naam:")
nameLabel.config(font=("Quicksand", 12))

nameEntry = Entry(leftMiddleFrame)
nameEntry.config(font=("Quicksand", 12))

startButton = Button(leftMiddleFrame, text="Start", width=15)
startButton.config(font=("Quicksand", 10))

leaderBoardButton = Button(leftMiddleFrame, text="Leaderboard", width=15)
leaderBoardButton.config(font=("Quicksand", 10))

# Grid config / layout
nameLabel.grid(row=1, column=0)
nameEntry.grid(row=1, column=1)
startButton.grid(row=2, column=0)
leaderBoardButton.grid(row=3)

root.mainloop()