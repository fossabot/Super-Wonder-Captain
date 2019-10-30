from tkinter import *
import math

def clicked():
    grondtal = int(entry.get())
    kwadraat = grondtal ** 2
    tekst = 'kwadraat: van {} = {}'
    label['text'] = tekst.format(grondtal, kwadraat)

def clicked2():
    grondtal = int(entry.get())
    wortel = math.sqrt(grondtal)
    tekst = 'wortel van {} = {}'
    label['text'] = tekst.format(grondtal, wortel)

root = Tk()

label = Label(master=root,
              text='Hello World',
              height=2)
label.pack()

button = Button(master=root, text='Kwadraat', command=clicked)
button.pack(side=LEFT, padx=10)

button2 = Button(master=root, text='Wortel', command=clicked2)
button2.pack(side=LEFT, pady=10)

entry = Entry(master=root)
entry.pack(padx=10, pady=10)

root.mainloop()

