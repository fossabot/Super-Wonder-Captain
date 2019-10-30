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
	comics=character['comics']['items']
	random.shuffle(comics)
	comicsNames=[]
	for comic in comics:
		comicsNames.append(comic['name'])
	return {'names':names,'description':description,'name':name,'comics':comicsNames}
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

#init_buffer()
#time.sleep(5)
#print(json.dumps(get_new_character(), indent=4, sort_keys=True), json.dumps(characterBuffer, indent=4, sort_keys=True))
def displayCharacter():
	character=get_new_character()
	for id in range(len(buttons)):
		buttons[id].config(text=character['names'][id])

def einde_spel(naam,score):
	timestamp=math.floor(time.time())
	cursor.execute('INSERT INTO scores(name, timestamp, score) VALUES (?,?,?);', (naam,timestamp,score))
	connection.commit()

def highscores():
	cursor.execute('SELECT * FROM scores ORDER BY scores.score DESC LIMIT 10;')
	data=cursor.fetchall()
	return data
#print(highscores())
init_buffer()
#time.sleep(3)
#print(json.dumps(sendMarvelRequest('comics/21366?'), indent=4, sort_keys=True))

# Tkinter GUI
def switchToGame():
	mainMenu.pack_forget()
	gameFrame.pack(expand=True, fill="both")
	displayCharacter()

def switchToMenu():
	gameFrame.pack_forget()
	mainMenu.pack(expand=True, fill="both")

def buttonClicked(id):
	print(id)

def nextQuestion():
	displayCharacter()

window = Tk()
window.title("Marvel Quiz")
mainMenu = Frame(window, height=800, width=1280)

# Main frame settings
window.resizable(width=False, height=False)
window.geometry('1280x800')
background_image = PhotoImage(file="marvel-login-screen.png")
background_label = Label(mainMenu, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

startFrame = Frame(mainMenu, bg="#fff")
startFrame.pack(side=LEFT, anchor=W, padx=(45, 0))

nameLabel = Label(startFrame, text="Naam:", bg="#fff")
nameLabel.config(font=("Quicksand", 12))

nameEntry = Entry(startFrame, bg="#fafafa", relief="groove", bd="2")
nameEntry.config(font=("Quicksand", 12))

startButton = Button(startFrame, text="START", width=15, command=switchToGame)
startButton.config(font=("Quicksand", 10, "bold"), bg="#202020", fg="#fff", bd="0")

leaderBoardButton = Button(startFrame, text="LEADERBOARD", width=15)
leaderBoardButton.config(font=("Quicksand", 10, "bold"), bg="#202020", fg="#fff", bd="0")

# Grid config / layout
nameLabel.grid(row=1, column=0, sticky=W)
nameEntry.grid(row=1, column=1, sticky=W, padx=(5, 0))
startButton.grid(row=2, column=0, sticky=W, pady=(60, 10), columnspan=2, ipadx=10, ipady=2)
leaderBoardButton.grid(row=3, column=0, sticky=W, columnspan=2, ipadx=10, ipady=2)

gameFrame = Frame(window, height=800, width=1280, bg="#fff")
gameFrame_background = PhotoImage(file="marvel-quiz-background.png")
gameFrame_background_label = Label(gameFrame, image=gameFrame_background)
gameFrame_background_label.place(x=0, y=0, relwidth=1, relheight=1)

menuButton = Button(gameFrame, text="MENU", command=switchToMenu)
menuButton.config(font=("Quicksand", 10, "bold"), bg="#202020", fg="#fff", bd="0")
menuButton.grid(row=2, column=0, sticky=W, pady=(60, 10), columnspan=2, ipadx=10, ipady=2)
buttons=[]
for i in range(10):
	actionButton=Button(gameFrame, text=str(i), command=lambda x=i: buttonClicked(x))
	actionButton.config(font=("Quicksand", 10, "bold"), bg="#202020", fg="#fff", bd="0")
	actionButton.grid(row=i, column=0, sticky=W, pady=(10, 10), columnspan=2, ipadx=10, ipady=2)
	buttons.append(actionButton)
buttons[0].config(text="abc")
switchToMenu()
window.mainloop()