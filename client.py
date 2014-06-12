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
        try: self.addr = sys.argv[1].split(':')
        except: print('Usage: client.py server_address[:port]'); quit()
        if len(self.addr) < 2: self.addr.append(25500)

        self.root = Tk()
        self.root.wm_title('Switchlight')
        self.root.after(1, self.loop)

        self.menubutton = Button(self.root, text="Menu", command = self.show_menu, font = tkFont.Font(size=16))
        self.menubutton.pack(anchor='w')

        self.switchframe = Frame(self.root)
        self.switchframe.pack(fill=BOTH, expand=1)

        self.switches = {}
        self.locked = False
        self.passcode = None

    def show_menu(self):
        self.menuwindow = Toplevel(self.root)
        self.lockbutton = Button(self.menuwindow, text="Lock", command = self.send_lock, font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.lockbutton.pack(fill=BOTH, expand=1)
        self.closebutton = Button(self.menuwindow, text="Close", command = self.menuwindow.destroy, font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.closebutton.pack()

    def send_lock(self):
        self.conn.send(['lock'])
        self.menuwindow.destroy()

    def send_unlock(self):
        print('passcode entered: ' + self.lockbox.get() + ' correct passcode: ' + str(self.passcode))
        if self.lockbox.get() == str(self.passcode):
            self.conn.send(['unlock'])
            self.locked = False
            self.unlock()
        else:
            self.lockbox.delete('0', END)
            self.locklabel.config(text="Incorrect passcode", fg='red')

    def lock(self):
        self.locked = True
        self.menubutton.pack_forget()
        self.switchframe.pack_forget()

        self.lockframe = Frame(self.root)
        self.lockframe.pack(fill=BOTH, expand=1)
        self.locklabel = Label(self.lockframe, text="Enter passcode to unlock")
        self.locklabel.grid(columnspan=3, sticky=N+S+E+W)
        self.lockbox = Entry(self.lockframe, show="*", font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.lockbox.grid(row=1, columnspan=3, sticky=N+S+E+W)

        for n in range(1, 10):
            Button(self.lockframe, text=str(n), command=lambda n=n: self.lockbox.insert(END, str(n)), font = tkFont.Font(size=16, weight=tkFont.BOLD)).grid(
                  row=((n-1)/3)+2, column=n-(3*((n-1)/3)+1), sticky=N+S+E+W)

        Button(self.lockframe, text='Clear', command=lambda: self.lockbox.delete('0', END), fg='red', font = tkFont.Font(size=12, weight=tkFont.BOLD)).grid(row=5, sticky=N+S+E+W)
        Button(self.lockframe, text='0', command=lambda: self.lockbox.insert(END, '0'), font = tkFont.Font(size=16, weight=tkFont.BOLD)).grid(row=5, column=1, sticky=N+S+E+W)
        Button(self.lockframe, text='Enter', command=self.send_unlock, fg='green', font = tkFont.Font(size=12, weight=tkFont.BOLD)).grid(row=5,column=2, sticky=N+S+E+W)

    def unlock(self):
        self.lockframe.pack_forget()
        self.menubutton.pack(anchor='w')
        self.switchframe.pack(fill=BOTH, expand=1)

    def run(self):
        self.conn = sockethandler.client(self.addr[0], self.addr[1])
        self.conn.send(['hi'])

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
                        self.switches[m[0]] = Switch(m[0], self.switchframe, self.conn)

                for m in msg[1]['sw']:
                    s = self.switches[m[0]]
                    if m[1] and not s.active:
                        print('switch ' + s.name + ' turned on.')
                        s.on()
                    elif not m[1] and s.active:
                        print('switch ' + s.name + ' turned off.')
                        s.off()

                if not self.passcode: self.passcode = msg[1]['l'][0]
                if msg[1]['l'][1] == True and not self.locked: self.lock()
                if msg[1]['l'][1] == False and self.locked: self.unlock()

            if msg[0] == 'bye':
                self.root.destroy()

        self.root.after(100, main.loop)



main = Main()
try:
    main.run()
except:
    main.conn.send(['bye'])
    main.conn.close()
    raise
