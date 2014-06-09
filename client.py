#!/usr/bin/env python
import sockethandler, time, sys, tkFont
from Tkinter import *

class Switch:
    def __init__(self, name, num, window, conn):
        self.name = name
        self.num = num
        self.button = Button(window, text = self.name, command = self.pressed, font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.button.config(fg = "red", activebackground = "white", bg = "white", activeforeground="red")
        self.button.pack(side=LEFT, fill=BOTH, expand=1)
        self.active = False
        self.conn = conn

    def pressed(self):
        print('button ' + self.name + ' pressed, is ' + str(self.active))
        if self.active:
            self.conn.send(['off', self.num])
        else:
            self.conn.send(['on', self.num])

    def on(self):
        self.button.config(fg="green", activeforeground="green")
        self.active = True

    def off(self):
        self.button.config(fg="red", activeforeground="red")
        self.active = False
    

try: addr = sys.argv[1].split(':')
except: print('Usage: client.py server_address[:port]'); quit()
if len(addr) < 2: addr.append(25500)
conn = sockethandler.client(addr[0], addr[1])
conn.send(['hi'])

def main():
    try:
        for msg in conn.recv():
            if msg[0] == 'hi':
                print('connected to server')
                for switch in msg[1:]:
                    switches.append(Switch(switch, len(switches), root, conn))
            if msg[0] == 'sw':
                for i in range(1, len(msg)):
                    s = switches[i-1]
                    if msg[i] and not s.active:
                        print('switch ' + s.name + ' turned on.')
                        s.on()
                    elif not msg[i] and s.active:
                        print('switch ' + s.name + ' turned off.')
                        s.off()
            if msg[0] == 'bye':
                root.destroy()
        root.after(100, main)
    except:
        conn.close()
        raise

switches = []
try:
    root = Tk()
    root.after(1, main)
    root.mainloop()
except:
    conn.send(['bye'])
    conn.close()
    raise

conn.close()
