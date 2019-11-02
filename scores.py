from datetime import datetime
import sqlite3
def connectSqlite():
	'maakt verbinding met de sqlite database. dit is in een aparte functie omdat dit meerdere keren wordt gebruikt. Sqlite kan niet vanaf meerdere threads gebruikt worden.'
	connection = sqlite3.connect('quiz.db')
	cursor = connection.cursor()
	return cursor,connection

cursor,connection=connectSqlite()
cursor.execute('CREATE TABLE IF NOT EXISTS `scores` (`name` TEXT,`timestamp` INT(10),`score` INT(3));')

def saveScore(naam,score):
	'slaat de score op in de SQLite database'
	timestamp = int(datetime.timestamp(datetime.now()))
	cursor,connection=connectSqlite()
	cursor.execute('INSERT INTO scores(name, timestamp, score) VALUES (?,?,?);', (naam, timestamp, score))
	connection.commit()

def formatDateTime(line,onlyToday):
	'zet de timestamp om naar een leesbaar formaat'
	line=list(line)
	if onlyToday:
		format="%H:%M:%S"
	else:
		format="%Y-%m-%d, %H:%M:%S"
	line[1]=datetime.fromtimestamp(line[1]).strftime(format)
	return line

def highScores(onlyToday):
	'haalt de dagelijkse highscores uit de database'
	if onlyToday:
		today = datetime.utcnow().date()
		startOfDay = datetime.timestamp(datetime(today.year, today.month, today.day))
	else:
		startOfDay=0
	cursor.execute(f'select * from scores where scores.timestamp>={startOfDay} ORDER BY scores.score DESC LIMIT 10;')
	data = cursor.fetchall()
	data=list(map(lambda line: formatDateTime(line,onlyToday),data))
	return data