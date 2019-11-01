import hashlib
import time
from tkinter import *
import json
import random
import threading
import re
import sqlite3
import math
import pyglet
import urllib.request
import urllib.parse
from PIL import Image, ImageTk
import io
from datetime import datetime

window = Tk()
#window.iconbitmap(r'marvelicon.bmp')
logo = PhotoImage(file='marvelicon.gif')
window.call('wm', 'iconphoto', window._w, logo)
pyglet.font.add_file('changa.ttf')
action_man = pyglet.font.load('Changa')

currentQuestion = None
score = 0
vragen_gesteld = 0
def connectSqlite():
	connection = sqlite3.connect('quiz.db')
	cursor = connection.cursor()
	return cursor,connection
cursor,connection=connectSqlite()
cursor.execute('CREATE TABLE IF NOT EXISTS `scores` (`name` TEXT,`timestamp` INT(10),`score` INT(3));')
questionBuffer = []
alltimeScoreBoardLabels=[]
dailyScoreBoardLabels=[]

user = ""

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

def guiData():
	'geeft de informatie die nodig is per character'
	character, characters = selectCharacter()
	name = character['name']
	beschrijving = character['description']
	names = selectNames(characters, name)
	replace_regex = re.compile(re.escape(name), re.IGNORECASE)  # zoeken zonder op hoofdletters te letten.
	description = replace_regex.sub('<naam>', character['description'])
	comics = character['comics']['items']
	random.shuffle(comics)
	comicsNames = []
	for comic in comics:
		comicsNames.append(comic['name'])
	urlpath = character['thumbnail']['path']
	urlextension = character['thumbnail']['extension']
	url = f"{urlpath}/portrait_uncanny.{urlextension}"
	print(url)
	raw_data = urllib.request.urlopen(url).read()
	img = raw_data
	return {'names': names, 'description': description, 'name': name, 'comics': comicsNames, 'img':img}

# print(guiData())
def bufferVraag():
	'zet de nieuwe vraag in de buffer.'
	questionBuffer.append(guiData())

def displayDescription():
	global score
	description.config(text=currentQuestion['description'])
	hintButton.config(state=DISABLED)
	score-=3
	displayScore()

def startBufferThread():
	threading.Thread(target=bufferVraag).start()


def nextQuestionData():
	'start download nieuwe vraag, en stuurt gegevens van buffer terug.'
	startBufferThread()
	return questionBuffer.pop()


def initBuffer():
	'download 2 vragen op de achtergrond'
	startBufferThread()
	startBufferThread()

def displayCharacter():
	'zet nieuwe vraag in het frame'
	global currentQuestion
	currentQuestion = nextQuestionData()
	for id in range(len(buttons)):
		buttons[id].config(text=currentQuestion['names'][id], bg="#4c4c4c")
		buttons[id].config(state='normal')
	for id in range(len(buttons)):
		buttons[id].config(text=currentQuestion['names'][id], bg="#4c4c4c")
		buttons[id].config(state='normal')
	image = ImageTk.PhotoImage(Image.open(io.BytesIO(currentQuestion['img'])))
	characterImage.config(image=image)
	characterImage.image=image

def saveScores():
	'slaat de score op in de SQLite database'
	naam=nameEntry.get()
	timestamp = math.floor(time.time())
	cursor,connection=connectSqlite()
	cursor.execute('INSERT INTO scores(name, timestamp, score) VALUES (?,?,?);', (naam, timestamp, score))
	connection.commit()

def dailyHighscores():
	'haalt de highscores uit de database'
	today = datetime.utcnow().date()
	startOfDay = datetime.timestamp(datetime(today.year, today.month, today.day))
	cursor.execute(f'select * from scores where scores.timestamp>={startOfDay} ORDER BY scores.score DESC LIMIT 10;')
	data = cursor.fetchall()
	return data
def alltimeHighscores():
	'haalt de highscores uit de database'
	cursor.execute('SELECT * FROM scores ORDER BY scores.score DESC LIMIT 10;')
	data = cursor.fetchall()
	return data

# Tkinter GUI
def newGame():
	'gameFrame in beeld brengen, score en aantal vragen beantwoord resetten'
	global score
	global vragen_gesteld
	vragen_gesteld = 0
	score = 0
	mainMenu.pack_forget()
	gameFrame.pack(expand=True, fill="both")
	nextQuestion()

def newGame2():
	'introFrame in beeld brengen, score en aantal vragen beantwoord resetten'
	global score
	global vragen_gesteld
	vragen_gesteld = 0
	score = 0
	introFrame.pack_forget()
	gameFrame.pack(expand=True, fill="both")
	nextQuestion()

def switchToIntro():
	global user
	mainMenu.pack_forget()
	introFrame.pack(expand=True, fill='both')
	user = nameEntry.get()
	introLabel.config(text=f'''Hoi {user}, welkom bij de quiz!
	Probeer met zo min mogelijk hints de superheld te raden.
	Je kan maximaal 15 punten per vraag krijgen.
	Je krijgt 3 minpunten voor een hint en 5 minpunten voor een fout antwoord.
	Succes!''')
	introLabel.config(font="Changa")

def einde_spel():
	global user
	gameFrame.pack_forget()
	endFrame.pack(expand=True, fill='both')
	user = nameEntry.get()
	endLabel.config(text=f'''Dit is het einde van de Quiz! Bedankt voor het spelen! 
Je hebt een score behaald van {score}''')
	endLabel.config(font="Changa")

def switchToMenu():
	'stopt spel, en gaat naar menu'
	leaderFrame.pack_forget()
	gameFrame.pack_forget()
	mainMenu.pack(expand=True, fill="both")

def switchToMenu2():
	introFrame.pack_forget()
	mainMenu.pack(expand=True, fill="both")

def switchToMenu3():
	endFrame.pack_forget()
	mainMenu.pack(expand=True, fill="both")

def displayScore():
	'update de score op het scherm.'
	scoreLabel.config(text="Score: "+str(score))

def switchToScoreboard():
	spelers=dailyHighscores()
	for index,speler in enumerate(spelers):
		date = datetime.fromtimestamp(speler[1]).strftime("%H:%M:%S")
		dailyScoreBoardLabels[index]['name'].config(text=speler[0])
		dailyScoreBoardLabels[index]['date'].config(text=date)
		dailyScoreBoardLabels[index]['score'].config(text=speler[2])
		spelers=alltimeHighscores()
	for index,speler in enumerate(spelers):
		date = datetime.fromtimestamp(speler[1]).strftime("%Y-%m-%d, %H:%M:%S")
		alltimeScoreBoardLabels[index]['name'].config(text=speler[0])
		alltimeScoreBoardLabels[index]['date'].config(text=date)
		alltimeScoreBoardLabels[index]['score'].config(text=speler[2])
	mainMenu.pack_forget()
	leaderFrame.pack(expand=True, fill="both")

def einde_spel():
	saveScores()
	global user
	gameFrame.pack_forget()
	endFrame.pack(expand=True, fill='both')
	user = nameEntry.get()
	endLabel.config(text=f'''Dit is het einde van de Quiz! Bedankt voor het spelen! 
Je hebt een score behaald van {score}''')
	endLabel.config(font="Changa")

def nieuwe_vraag_delay():
	'wacht een seconden, en geeft de volgende vraag, of stopt het spel.'
	time.sleep(1)
	if (vragen_gesteld == 10):
		einde_spel()
	else:
		nextQuestion()


def buttonClicked(id):
	'wordt uitgevoerd wanneer er een antwoord wordt gegeven, controlleert of het antwoord goed is, en update de punten wanneer nodig'
	global score
	nameClicked = currentQuestion['names'][id]
	correct = currentQuestion['name']
	if correct == nameClicked:
		buttons[id].config(bg="#00FF00")
		score += 15
		for buttonId in range(len(buttons)):
			buttons[buttonId].config(state=DISABLED)
		threading.Thread(target=nieuwe_vraag_delay).start()
	else:
		buttons[id].config(state=DISABLED)
		buttons[id].config(bg="#FF0000")
		score -= 5
	displayScore()

def nextQuestion():
	'geeft de volgende vraag, en update de punten'
	global score
	global vragen_gesteld
	vragen_gesteld += 1
	displayCharacter()
	displayScore()
	displayAantalvragen()
	description.config(text="")
	hintButton.config(state='normal')
	

def displayAantalvragen():
    aantalvragen.config(text="Vraag "+str(vragen_gesteld)+"/10")

window.title("Marvel Quiz")
mainMenu = Frame(window, height=800, width=1280)
# mainMenu = Frame(window, height=768, width=1280)

# Main frame settings
window.resizable(width=False, height=False)
window.geometry('1280x800')
background_image = PhotoImage(file="marvel-login-screen.png")
background_label = Label(mainMenu, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

startFrame = Frame(mainMenu, bg="#fff")
startFrame.pack(side=LEFT, anchor=W, padx=(45, 0))

nameLabel = Label(startFrame, text="Naam:", bg="#fff")
nameLabel.config(font=("Changa", 12))

nameEntry = Entry(startFrame, bg="#fafafa", relief="groove", bd="2")
nameEntry.config(font=("Changa", 12))

startButton = Button(startFrame, text="START", width=15, command=switchToIntro)
startButton.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")

leaderBoardButton = Button(startFrame, text="LEADERBOARD", width=15, command=switchToScoreboard)
leaderBoardButton.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")

# Grid config / layout
nameLabel.grid(row=1, column=0, sticky=W)
nameEntry.grid(row=1, column=1, sticky=W, padx=(5, 0))
startButton.grid(row=2, column=0, sticky=W, pady=(60, 8), columnspan=2, ipadx=10, ipady=2)
leaderBoardButton.grid(row=3, column=0, sticky=W, pady=(5, 8), columnspan=2, ipadx=10, ipady=2)

introFrame = Frame(window, height=800, width=1280, bg="#fff")
introFrame_background = PhotoImage(file="marvel-login-screen.png")
introFrame_background_label = Label(introFrame, image=introFrame_background)
introFrame_background_label.place(x=0, y=0, relwidth=1, relheight=1)
introLabel = Label(master=introFrame, bg='white', height=5)
introLabel.place(relx=0.21, rely=0.65, anchor=CENTER)

endFrame = Frame(window, height=800, width=1280, bg="#fff")
endFrame_background = PhotoImage(file="stan-lee-positieve-score.png")
endFrame_background_label = Label(endFrame, image=endFrame_background)
endFrame_background_label.place(x=0, y=0, relwidth=1, relheight=1)
endLabel = Label(master=endFrame, bg='white', height=5)
endLabel.place(relx=0.21, rely=0.55, anchor=CENTER)

menuButton2 = Button(introFrame, text="TERUG NAAR MENU", command=switchToMenu2)
menuButton2.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")
menuButton2.place(relx=0.25, rely=0.45)

menuButton3 = Button(endFrame, text="TERUG NAAR MENU", command=switchToMenu3)
menuButton3.config(font=("Changa", 10, "bold"), bg="#ED1D24", fg="#fff", bd="0")
menuButton3.place(relx=0.15, rely=0.60)

startButton2 = Button(introFrame, text="START SPEL", width=15, command=newGame2)
startButton2.config(font=("Changa", 10, "bold"), bg="#ED1D24", fg="#fff", bd="0")
startButton2.place(relx=0.13, rely=0.45)

gameFrame = Frame(window, height=800, width=1280, bg="#fff")
gameFrame_background = PhotoImage(file="marvel-quiz-background.png")
gameFrame_background_label = Label(gameFrame, image=gameFrame_background)
gameFrame_background_label.place(x=0, y=0, relwidth=1, relheight=1)

menuButton = Button(gameFrame, text="MENU", command=switchToMenu)
menuButton.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0")
menuButton.place(relx=0.02, rely=0.02)

questionContainer = Label(gameFrame, bg="#f4f4f4")
questionContainer.place(relx=0.20, rely=0.25)

buttons = []
for i in range(10):
	actionButton = Button(questionContainer, text=str(i), command=lambda x=i: buttonClicked(x), anchor=CENTER)
	actionButton.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#fff", bd="0")
	actionButton.grid(row=i, pady=(5, 5))
	buttons.append(actionButton)

description = Label(gameFrame, text="<DESC>")
description.place(relx=0.15, rely=0.1, anchor=CENTER)
description.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0")
hintButton = Button(gameFrame, text="Hint (-3 Punten)",command=displayDescription)
hintButton.place(relx=0.6, rely=0.04)
hintButton.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0", borderwidth=2, relief="groove")
aantalvragen = Label(gameFrame, text="<VRAGEN>")
aantalvragen.place(relx=0.5, rely=0.9, anchor=CENTER)
aantalvragen.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0")
scoreLabel = Label(gameFrame, text="<SCORE>")
scoreLabel.place(relx=0.02, rely=0.9, anchor=W)
scoreLabel.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0")

characterImage = Label(gameFrame, image=PhotoImage(file="marvel-login-screen.png"))
characterImage.place(rely=0.25, relx=0.55)

leaderFrame = Frame(window, height=800, width=1280, bg="#fff")
leaderFrameBackgroundImage = PhotoImage(file="marvel-quiz-background.png")
leaderFrameBackgroundLabel = Label(leaderFrame, image=leaderFrameBackgroundImage)
leaderFrameBackgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)
leaderFrameBackButton = Button(leaderFrame, text="MENU", command=switchToMenu)
leaderFrameBackButton.config(font=("Changa", 10, "bold"), bg="#f4f4f4", fg="#6c6c6c", bd="0")
leaderFrameBackButton.place(relx=0.02, rely=0.02)
dailyleaderFrameGrid=Frame(leaderFrame, bg="#f4f4f4", borderwidth=2, relief="groove")
dailyleaderFrameGrid.place(relx=0.05,rely=0.2)
dailyleaderBoardName=Label(dailyleaderFrameGrid,text="Naam", bg="#f4f4f4", fg="#6c6c6c")
dailyleaderBoardName.grid(row=0,column=1)
dailyleaderBoardDate=Label(dailyleaderFrameGrid,text="Datum", bg="#f4f4f4", fg="#6c6c6c")
dailyleaderBoardDate.grid(row=0,column=2)
dailyleaderBoardScore=Label(dailyleaderFrameGrid,text="Score", bg="#f4f4f4", fg="#6c6c6c")
dailyleaderBoardScore.grid(row=0,column=3)
alltimeleaderFrameGrid=Frame(leaderFrame, bg="#f4f4f4", borderwidth=2, relief="groove")
alltimeleaderFrameGrid.place(relx=0.3,rely=0.2)
alltimeleaderBoardName=Label(alltimeleaderFrameGrid,text="Naam", bg="#f4f4f4", fg="#6c6c6c")
alltimeleaderBoardName.grid(row=0,column=1)
alltimeleaderBoardDate=Label(alltimeleaderFrameGrid,text="Datum", bg="#f4f4f4", fg="#6c6c6c")
alltimeleaderBoardDate.grid(row=0,column=2)
alltimeleaderBoardScore=Label(alltimeleaderFrameGrid,text="Score", bg="#f4f4f4", fg="#6c6c6c")
alltimeleaderBoardScore.grid(row=0,column=3)
dailyLabel = Label(leaderFrame, text="Dagelijks:", bg="#fff")
dailyLabel.config(font=("Changa", 12), bg="#f4f4f4", fg="#6c6c6c")
dailyLabel.place(relx=0.05, rely=0.15)
alltimeLabel = Label(leaderFrame, text="Top Highscores:")
alltimeLabel.config(font=("Changa", 12), bg="#f4f4f4", fg="#6c6c6c")
alltimeLabel.place(relx=0.3, rely=0.15)


for i in range(1,11):
	leaderBoardName=Label(dailyleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardName.grid(row=i,column=1,padx=(10,10))
	leaderBoardDate=Label(dailyleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardDate.grid(row=i,column=2,padx=(10,10))
	leaderBoardScore=Label(dailyleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardScore.grid(row=i,column=3,padx=(10,10))
	dailyScoreBoardLabels.append({"name":leaderBoardName,"date":leaderBoardDate,"score":leaderBoardScore})
	leaderBoardName=Label(alltimeleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardName.grid(row=i,column=1,padx=(10,10))
	leaderBoardDate=Label(alltimeleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardDate.grid(row=i,column=2,padx=(10,10))
	leaderBoardScore=Label(alltimeleaderFrameGrid,text="", bg="#f4f4f4", fg="#6c6c6c")
	leaderBoardScore.grid(row=i,column=3,padx=(10,10))
	alltimeScoreBoardLabels.append({"name":leaderBoardName,"date":leaderBoardDate,"score":leaderBoardScore})

initBuffer()
switchToMenu()
window.mainloop()