import sockethandler, time, sys
from Tkinter import *

class Switch:
    def __init__(self, name, num, window, conn):
        self.name = name
        self.num = num
        self.button = Button(window, text = self.name, command = self.pressed)
        self.button.pack(side=LEFT, fill=BOTH)
        self.active = False
        self.conn = conn

    def pressed(self):
        print('button ' + self.name + ' pressed')
        if self.active:
            self.conn.send(['on', self.num])
        else:
            self.conn.send(['off', self.num])

    def on(self):
        self.button.config(state = ACTIVE)
        self.active = True

    def off(self):
        self.button.config(state = NORMAL)
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
                for status in msg[1:]:
                    if status and switches[msg.index(status)-1].active:
                        print('switch ' + switches[msg.index(status)-1].name + ' turned off.')
                        switches[msg.index(status)-1].off()
                    elif not status and not switches[msg.index(status)-1].active:
                        print('switch ' + switches[msg.index(status)-1].name + ' turned on.')
                        switches[msg.index(status)-1].on()

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
