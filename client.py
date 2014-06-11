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


class Main:
    def __init__(self):
        try: addr = sys.argv[1].split(':')
        except: print('Usage: client.py server_address[:port]'); quit()
        if len(addr) < 2: addr.append(25500)

        self.conn = sockethandler.client(addr[0], addr[1])
        self.conn.send(['hi'])

        self.root = Tk()
        self.root.wm_title('Switchlight')
        self.root.after(1, self.loop)

        self.switches = {}
        self.locked = False

    def run(self):
        self.root.mainloop()
        self.conn.send(['bye'])
        self.conn.close()

    def loop(self):
        for msg in self.conn.recv():
            if msg[0] == 'hb':
                self.conn.send(['hb'])

            if msg[0] == 's':
                if not [s[0] for s in msg[1]['sw']] == [s.name for s in self.switches.values()]:
                    for sw in self.switches.values(): 
                        sw.button.pack_forget()
                        del self.switches[sw.name]
                    for m in msg[1]['sw']:
                        self.switches[m[0]] = Switch(m[0], self.root, self.conn)

                for m in msg[1]['sw']:
                    s = self.switches[m[0]]
                    if m[1] and not s.active:
                        print('switch ' + s.name + ' turned on.')
                        s.on()
                    elif not m[1] and s.active:
                        print('switch ' + s.name + ' turned off.')
                        s.off()

            if msg[0] == 'bye':
                self.root.destroy()

        self.root.after(100, main)


try:
    main = Main()
    main.run()
except:
    conn.send(['bye'])
    conn.close()
    raise
