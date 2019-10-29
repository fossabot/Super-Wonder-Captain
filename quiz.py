import requests
import hashlib
import time
from tkinter import *
import json

def sendMarvelRequest(request):
	loginInfo=json.load(open('apikey.json','r'))
	stamp=str(time.time())
	pubkey=loginInfo['pubkey']
	privatekey=loginInfo['privatekey']
	hashString=stamp+privatekey+pubkey
	hash=hashlib.md5(hashString.encode()).hexdigest()
	httprequest=requests.get(f'http://gateway.marvel.com/v1/public/{request}?ts={stamp}&apikey={pubkey}&hash={hash}')
	return json.loads(httprequest.text)['data']['results']
#print(sendMarvelRequest('characters'))

class Window(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master


root = Tk()
app = Window(root)
root.mainloop()
