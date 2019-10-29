import requests
import hashlib
import time
from tkinter import *
import json
public='05e07ce2914b79046f157b3f7eee36b3'
private='c1e103dcdbd9d9c0bec980663077e52b346317e2'

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master


root = Tk()
app = Window(root)
root.mainloop()
