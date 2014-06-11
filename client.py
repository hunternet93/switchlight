#!/usr/bin/env python
import sockethandler, time, sys, tkFont
from Tkinter import *

class Switch:
    def __init__(self, name, window, conn):
        self.name = name
        self.button = Button(window, text = self.name, command = self.pressed, font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.button.config(fg = "red", activebackground = "white", bg = "white", activeforeground="red")
        self.button.pack(side=LEFT, fill=BOTH, expand=1)
        self.active = False
        self.conn = conn

    def pressed(self):
        print('button ' + self.name + ' pressed, is ' + str(self.active))
        if self.active:
            self.conn.send(['off', self.name])
        else:
            self.conn.send(['on', self.name])

    def on(self):
        self.button.config(fg="green", activeforeground="green")
        self.active = True

    def off(self):
        self.button.config(fg="red", activeforeground="red")
        self.active = False
    

try: addr = sys.argv[1].split(':')
except: print('Usage: client.py server_address[:port]'); quit()
if len(addr) < 2: addr.append(25500)

while True:
    try:
        conn = sockethandler.client(addr[0], addr[1])
        conn.send(['hi'])
        break
    except socket.error:
        time.sleep(2.5)

def main():
    try:
        for msg in conn.recv():
            if msg[0] == 'hb':
                conn.send(['hb'])

            if msg[0] == 's':
                if not [s[0] for s in msg[1]['sw']] == [s.name for s in switches.values()]:
                    for sw in switches.values(): 
                        sw.button.pack_forget()
                        del switches[sw.name]
                    for m in msg[1]['sw']:
                        switches[m[0]] = Switch(m[0], root, conn)

                for m in msg[1]['sw']:
                    s = switches[m[0]]
                    if m[1] and not s.active:
                        print('switch ' + s.name + ' turned on.')
                        s.on()
                    elif not m[1] and s.active:
                        print('switch ' + s.name + ' turned off.')
                        s.off()

            if msg[0] == 'bye':
                root.destroy()

        root.after(100, main)

    except:
        conn.close()
        raise

switches = {}
try:
    root = Tk()
    root.wm_title('Switchlight')
    root.after(1, main)
    root.mainloop()
except:
    conn.send(['bye'])
    conn.close()
    raise

conn.send(['bye'])
conn.close()
