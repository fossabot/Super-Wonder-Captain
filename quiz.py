import time
import threading
from tkinter.messagebox import showinfo
from API import bufferVraag,getQuestion
from scores import highScores,saveScore
import pdb
currentQuestion = None
score = 0
vragen_gesteld = 0
user = ""
def switchToIntro():
	'switcht naar de intro, en update de naam die wordt weergegeven.'
	global user
	user = getName()
	if(len(user)==0):
		showinfo("Naam", "Voer een naam in.")
		return
	showFrame('introFrame')
	setText('introLabel',f'''Hoi {user}, welkom bij de quiz!
	Probeer met zo min mogelijk hints de superheld te raden.
	Je kan maximaal 15 punten per vraag krijgen.
	Je krijgt 3 minpunten voor een hint en 5 minpunten voor een fout antwoord.
	Succes!''')

def switchToMenu():
	'gaat naar menu'
	showFrame('mainMenu')
def switchToScoreboard():
	'update het scoreboard, en geeft de informatie weer.'
	spelers=highScores(True)
	for index,speler in enumerate(spelers):
		setText(f'dailyScoreBoardLabels[{index}]["name"]',speler[0])
		setText(f'dailyScoreBoardLabels[{index}]["date"]',speler[1])
		setText(f'dailyScoreBoardLabels[{index}]["score"]',speler[2])
	spelers=highScores(False)
	for index,speler in enumerate(spelers):
		setText(f'alltimeScoreBoardLabels[{index}]["name"]',speler[0])
		setText(f'alltimeScoreBoardLabels[{index}]["date"]',speler[1])
		setText(f'alltimeScoreBoardLabels[{index}]["score"]',speler[2])
	showFrame('leaderFrame')

def displayDescription():
	global score
	setText('description',currentQuestion['description'])
	setDisabled('hintButton',True)
	score-=3
	displayScore()

def startBufferThread():
	threading.Thread(target=bufferVraag).start()

def nextQuestionData():
	'start download nieuwe vraag, en stuurt gegevens van buffer terug.'
	startBufferThread()
	return getQuestion()


def initBuffer():
	'download 2 vragen op de achtergrond'
	startBufferThread()
	startBufferThread()

def displayCharacter():
	'zet nieuwe vraag in het frame'
	global currentQuestion
	currentQuestion = nextQuestionData()
	for id in range(10):
		setText(f'buttons[{id}]',currentQuestion['names'][id])
		setBg(f'buttons[{id}]',"#4c4c4c")
		setDisabled(f'buttons[{id}]',False)
	image = currentQuestion['img']
	setImage('characterImage',image)

def newGame():
	'introFrame in beeld brengen, score en aantal vragen beantwoord resetten'
	global score
	global vragen_gesteld
	vragen_gesteld = 0
	score = 0
	showFrame('gameFrame')
	nextQuestion()
	
def displayScore():
	'update de score op het scherm.'
	setText('scoreLabel',f"Score: {score}")

def einde_spel():
	'slaat de score op, en geeft het eindframe'
	saveScore(user, score)
	showFrame('endFrame')
	setText('endLabel',f'''Dit is het einde van de Quiz! Bedankt voor het spelen! 
Je hebt een score behaald van {score}''')

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
		setBg(f'buttons[{id}]',"#00FF00")
		score += 15
		for buttonId in range(10):
			setDisabled(f'buttons[{buttonId}]',True)
		threading.Thread(target=nieuwe_vraag_delay).start()
	else:
		setDisabled(f'buttons[{id}]',True)
		setBg(f'buttons[{id}]',"#FF0000")
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
	setText('description','')
	setDisabled('hintButton',False)
	

def displayAantalvragen():
	'geeft het aantal vragen rechtsonder weer'
	setText('aantalvragen',"Vraag "+str(vragen_gesteld)+"/10")
from GUI import getName,returnGUIVariables,showFrame,setText,setDisabled,setBg,setImage
if __name__ == '__main__':
	description,buttons,introLabel,scoreLabel,dailyScoreBoardLabels,alltimeScoreBoardLabels,endLabel,window=returnGUIVariables()
	print(dailyScoreBoardLabels)
	initBuffer()
	switchToMenu()
	window.mainloop()