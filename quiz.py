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
import pyglet
window=Tk()

window.iconbitmap(r'marvelicon.ico')
pyglet.font.add_file('changa.ttf')
action_man = pyglet.font.load('Changa')

currentQuestion = None
score = 0
vragen_gesteld = 0
connection = sqlite3.connect('quiz.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS `scores` (`name` TEXT,`timestamp` INT(10),`score` INT(3));')
questionBuffer = []
user = ""


def sendMarvelRequest(request):
    'stuurt een aanvraag naar de Marvel API'
    loginInfo = json.load(open('apikey.json', 'r'))
    stamp = str(time.time())
    pubkey = loginInfo['pubkey']
    privatekey = loginInfo['privatekey']
    hashString = stamp + privatekey + pubkey
    hash = hashlib.md5(hashString.encode()).hexdigest()
    httprequest = requests.get(f'https://gateway.marvel.com/v1/public/{request}&ts={stamp}&apikey={pubkey}&hash={hash}')
    return json.loads(httprequest.text)['data']['results']


def selectCharacter():
    'selecteert een willekeurig character die een beschrijving heeft'
    while True:
        randomNumber = random.randint(0, 1400)
        characters = sendMarvelRequest(f'characters?offset={randomNumber}&orderBy=modified')
        for character in characters:
            if len(character['description']) > 0:
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
    names = selectNames(characters, name)
    replace_regex = re.compile(re.escape(name), re.IGNORECASE)  # zoeken zonder op hoofdletters te letten.
    description = replace_regex.sub('<naam>', character['description'])
    comics = character['comics']['items']
    random.shuffle(comics)
    comicsNames = []
    for comic in comics:
        comicsNames.append(comic['name'])
    return {'names': names, 'description': description, 'name': name, 'comics': comicsNames}


# print(guiData())
def bufferVraag():
    'zet de nieuwe vraag in de buffer.'
    questionBuffer.append(guiData())


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


# TODO: afbeelding weergeven

def saveScores(naam, score):
    'slaat de score op in de SQLite database'
    timestamp = math.floor(time.time())
    cursor.execute('INSERT INTO scores(name, timestamp, score) VALUES (?,?,?);', (naam, timestamp, score))
    connection.commit()


def highscores():
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

def switchToMenu():
    'stopt spel, en gaat naar menu'
    gameFrame.pack_forget()
    mainMenu.pack(expand=True, fill="both")


def displayScore():
    'update de score op het scherm.'
    scoreLabel.config(text=score)


def nieuwe_vraag_delay():
    'wacht een seconden, en geeft de volgende vraag, of stopt het spel.'
    time.sleep(1)
    if (vragen_gesteld == 10):
        einde_spel()  # TODO
    else:
        nextQuestion()


def buttonClicked(id):
    'wordt uitgevoerd wanneer er een antwoord wordt gegeven, controlleert of het antwoord goed is, en update de punten wanneer nodig'
    global score
    nameClicked = currentQuestion['names'][id]
    correct = currentQuestion['name']
    if correct == nameClicked:
        buttons[id].config(bg="#00FF00")
        threading.Thread(target=nieuwe_vraag_delay).start()
    else:
        buttons[id].config(bg="#FF0000")
        score -= 5
    displayScore()


def nextQuestion():
    'geeft de volgende vraag, en update de punten'
    global score
    global vragen_gesteld
    vragen_gesteld += 1
    score += 15
    displayCharacter()
    displayScore()


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

startButton = Button(startFrame, text="START", width=15, command=newGame)
startButton.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")

leaderBoardButton = Button(startFrame, text="LEADERBOARD", width=15)
leaderBoardButton.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")

introButton = Button(startFrame, text="INTRO", width=15, command=switchToIntro)
introButton.config(font=("Changa", 10, "bold"), bg="#4c4c4c", fg="#fff", bd="0")

# Grid config / layout
nameLabel.grid(row=1, column=0, sticky=W)
nameEntry.grid(row=1, column=1, sticky=W, padx=(5, 0))
startButton.grid(row=2, column=0, sticky=W, pady=(60, 8), columnspan=2, ipadx=10, ipady=2)
leaderBoardButton.grid(row=3, column=0, sticky=W, pady=(5, 8), columnspan=2, ipadx=10, ipady=2)
introButton.grid(row=4, column=0, sticky=W, pady=(5, 8), columnspan=2, ipadx=10, ipady=2)

introFrame = Frame(window, height=800, width=1280, bg="#fff")
introFrame_background = PhotoImage(file="marvel-login-screen.png")
introFrame_background_label = Label(introFrame, image=introFrame_background)
introFrame_background_label.place(x=0, y=0, relwidth=1, relheight=1)
introLabel = Label(master=introFrame, bg='white', height=5)
introLabel.place(relx=0.05, rely=0.5, anchor=W)

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
scoreLabel = Label(gameFrame, text="<SCORE>")
scoreLabel.place(relx=0, rely=0.9, anchor=W)

initBuffer()
switchToMenu()
window.mainloop()