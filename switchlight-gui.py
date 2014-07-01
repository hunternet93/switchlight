#!/usr/bin/env python
import switchlight_api
import math
import time
import tkFont
from Tkinter import *

class SwitchButton:
    def __init__(self, parent, switch):
        self.parent = parent
        self.switch = switch
        self.switch.on = self.on
        self.switch.off = self.off

        self.name = self.switch.name
        self.button = Button(self.parent, text = self.name, command = self.pressed, 
                             font = tkFont.Font(size = 20, weight = tkFont.BOLD),
                             fg = "red", activebackground = "white", bg = "white",
                             activeforeground = "red")

        if self.switch.active: self.on()

    def pressed(self):
        self.switch.set(not self.switch.active)

    def on(self):
        self.button.config(fg = "green", activeforeground = "green")

    def off(self):
        self.button.config(fg = "red", activeforeground = "red")

class TimerWidget:
    def __init__(self, parent, timer, cancel, row):
        self.parent = parent
        self.timer = timer

        acttime = time.strftime('%I:%M:%S %p', time.localtime(timer.time))
        self.timelabel = Label(self.parent, font = tkFont.Font(size = 16),
                               text = acttime)
        self.timelabel.grid(row = row)

        actions = ''
        for a in self.timer.action.items():
            state = 'On' if a[1] else 'Off'
            actions += a[0] + ' ' + state + '\n'
        if timer.lock: actions += 'Lock Switchlight\n'

        self.actionslabel = Label(self.parent, font = tkFont.Font(size = 16),
                                  text = actions)
        self.actionslabel.grid(row = row, column = 2, sticky = N+S+E+W)

        self.cancelbutton = Button(self.parent, font = tkFont.Font(size = 16),
                                   fg = 'red', command = lambda: cancel(self.timer),
                                   text = 'Cancel')
        self.cancelbutton.grid(row = row, column = 3)

    def hide(self):
        self.timelabel.grid_forget()
        self.actionslabel.grid_forget()
        self.cancelbutton.grid_forget()


class MessageFrame:
    def __init__(self, main):
        self.message = Label(main.root, font = tkFont.Font(size = 20, weight = tkFont.BOLD))

    def set_message(self, message):
        self.message.config(text = message)

    def show(self):
        self.message.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.message.pack_forget()


class SwitchFrame:
    def __init__(self, main):
        self.main = main
        self.frame = Frame(self.main.root)

        self.menubutton = Button(self.frame, text="Menu", command = lambda: self.main.set_frame('menu'), font = tkFont.Font(size=16))
        self.menubutton.pack(anchor = 'w')

        self.switchframe = Frame(self.frame)
        self.switchframe.pack(fill = BOTH, expand = 1)

        self.switchbuttons = []

    def init_switches(self, switches):
        for switch in switches.values():
            self.switchbuttons.append(SwitchButton(self.switchframe, switch))

        # The author sincerely apoligizes for the below line.
        rows, columns = int(round(math.sqrt(len(self.switchbuttons)))), int(math.ceil(len(self.switchbuttons)/round(math.sqrt(len(self.switchbuttons)))))
        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                try:
                    self.switchbuttons.pop(0).button.grid(row=row, column=column, sticky=N+S+E+W)
                    self.switchframe.grid_rowconfigure(row, weight=1)
                    self.switchframe.grid_columnconfigure(column, weight=1)
                except IndexError: break

    def show(self):
        self.frame.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.frame.pack_forget()


class MenuFrame:
    def __init__(self, main):
        self.main = main
        self.frame = Frame(self.main.root)
        self.lockbutton = Button(self.frame, text="Lock", command = self.main.sl.lock,
                                 font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.lockbutton.pack(fill=BOTH, expand=1)
        self.timerbutton = Button(self.frame, text="Timers", command = lambda: self.main.set_frame('timers'),
                                  font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.timerbutton.pack(fill=BOTH, expand=1)
        self.closebutton = Button(self.frame, text="Close", command = lambda: self.main.set_frame('switch'),
                                  font = tkFont.Font(size=20, weight=tkFont.BOLD))
        self.closebutton.pack()

    def show(self):
        self.frame.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.frame.pack_forget()


class LockFrame:
    def __init__(self, main):
        self.main = main
        self.lockframe = Frame(self.main.root)
        self.locklabel = Label(self.lockframe, text="Enter passcode to unlock")
        self.locklabel.grid(columnspan=3, sticky=N+S+E+W)
        self.lockbox = Entry(self.lockframe, show="*", font = tkFont.Font(size=24, weight=tkFont.BOLD))
        self.lockbox.grid(row=1, columnspan=3, sticky=N+S+E+W)

        for n in range(1, 10):
            Button(self.lockframe, text=str(n), command=lambda n=n: self.lockbox.insert(END, str(n)), font = tkFont.Font(size=20, weight=tkFont.BOLD),
                  activebackground = "grey", bg = "grey").grid(row=((n-1)/3)+2, column=n-(3*((n-1)/3)+1), sticky=N+S+E+W)

        Button(self.lockframe, text='Clear', command=lambda: self.lockbox.delete('0', END), fg='red', activebackground = "grey", bg = "grey",
               font = tkFont.Font(size=20, weight=tkFont.BOLD)).grid(row=5, sticky=N+S+E+W)
        Button(self.lockframe, text='0', command=lambda: self.lockbox.insert(END, '0'), activebackground = "grey", bg = "grey", 
               font = tkFont.Font(size=20, weight=tkFont.BOLD)).grid(row=5, column=1, sticky=N+S+E+W)
        Button(self.lockframe, text='Enter', command=self.test_unlock, fg='green', activebackground = "grey", bg = "grey",
               font = tkFont.Font(size=20, weight=tkFont.BOLD)).grid(row=5,column=2, sticky=N+S+E+W)

        self.lockframe.grid_rowconfigure(1, weight=1)
        for n in range(2,6): self.lockframe.grid_rowconfigure(n, weight=2)
        for n in range(0,3): self.lockframe.grid_columnconfigure(n, weight=1)

    def test_unlock(self):
        if self.main.sl.unlock(self.lockbox.get()):
            self.main.set_frame('switch')
        else:
            self.lockbox.delete('0', END)
            self.locklabel.config(text="Incorrect passcode", fg='red')

    def show(self):
        self.lockframe.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.lockbox.delete('0', END)
        self.lockframe.pack_forget()


class TimersFrame:
    def __init__(self, main):
        self.main = main
        self.frame = Frame(self.main.root)

        self.timersframe = Frame(self.frame)
        self.timersframe.pack(expand = 1, fill = BOTH)

        self.timersframe.grid_columnconfigure(2, weight=2)

        Label(self.timersframe, text = 'Time',
              font = tkFont.Font(size = 16, weight = tkFont.BOLD)).grid()
        Label(self.timersframe, text = 'Actions',
              font = tkFont.Font(size = 16, weight = tkFont.BOLD)).grid(row = 0, column = 1)

        self.buttonframe = Frame(self.frame)
        self.buttonframe.pack(expand = 1, fill = Y)
        Button(self.buttonframe, text='Close', command = lambda: self.main.set_frame('switch'),
               font = tkFont.Font(size = 20, weight = tkFont.BOLD)).pack(side = LEFT, anchor = 's')
        Button(self.buttonframe, text='Set Timer', command = lambda: self.main.set_frame('settimer'),
               font = tkFont.Font(size = 20, weight = tkFont.BOLD)).pack(side = LEFT, anchor = 's')

        self.main.sl.on_timer_added = self.main.sl.on_timer_removed = self.on_timers_change

        self.timerwidgets = []

        self.shown = False

    def on_timers_change(self, timer):
        if self.shown: self.generate_list()

    def generate_list(self):
        for t in self.timerwidgets: t.hide()
        del self.timerwidgets[:]

        timers = self.main.sl.get_timers().values()
        timers = sorted(timers, key=lambda timer: timer.time)

        for n in range(0, len(timers)):
            self.timerwidgets.append(TimerWidget(self.timersframe, timers[n],
                                                 self.main.sl.cancel_timer, n + 1))

    def show(self):
        self.shown = True
        self.generate_list()
        self.frame.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.shown = False
        self.frame.pack_forget()
        

class SetTimerFrame:
    def __init__(self, main):
        self.main = main
        self.frame = Frame(self.main.root)

        self.timerleftframe = Frame(self.frame)
        self.timerleftframe.pack(side=LEFT, fill=BOTH, expand=1)

        Label(self.timerleftframe, text="Turn selected switches:", font = tkFont.Font(size=16, weight=tkFont.BOLD)).pack(fill=BOTH,expand=1)

        self.timermodevar = BooleanVar()
        Radiobutton(self.timerleftframe, text='On', variable=self.timermodevar, value=True, font = tkFont.Font(size=16, weight=tkFont.BOLD)).pack(fill=BOTH,expand=1)
        Radiobutton(self.timerleftframe, text='Off', variable=self.timermodevar, value=False, font = tkFont.Font(size=16, weight=tkFont.BOLD)).pack(fill=BOTH,expand=1)

        self.switchbox = Listbox(self.timerleftframe, selectmode=MULTIPLE, font = tkFont.Font(size=16, weight=tkFont.BOLD))
        self.switchbox.pack(fill=BOTH, expand=1)

        self.timerrightframe = Frame(self.frame)
        self.timerrightframe.pack(side=LEFT, expand=1, fill=BOTH)
        self.lockvar = IntVar()
        Checkbutton(self.timerrightframe, text='Lock', variable=self.lockvar, font = tkFont.Font(size=16, weight=tkFont.BOLD)).pack(fill=BOTH,expand=1)

        Label(self.timerrightframe, text='Set switches in', font = tkFont.Font(size=16, weight=tkFont.BOLD)).pack(fill=BOTH, expand=1)
        self.hourscale = Scale(self.timerrightframe, label='Hours', from_=0, to=23, orient=HORIZONTAL, font = tkFont.Font(size=16, weight=tkFont.BOLD))
        self.hourscale.pack(fill=BOTH,expand=1)
        self.minutescale = Scale(self.timerrightframe, label='Minutes', from_=1, to=59, orient=HORIZONTAL, font = tkFont.Font(size=16, weight=tkFont.BOLD))
        self.minutescale.pack(fill=BOTH,expand=1)

        Button(self.timerleftframe, text='Cancel', command=lambda: self.main.set_frame('switch'),
               fg='red', font = tkFont.Font(size=20, weight=tkFont.BOLD)).pack(expand=1, anchor='s')
        Button(self.timerrightframe, text='Set Timer', command=self.timer_set,
               fg='green', font = tkFont.Font(size=20, weight=tkFont.BOLD)).pack(expand=1, anchor='s')

    def timer_set(self):
        switches = [self.switchbox.get(0,END)[int(i)] for i in self.switchbox.curselection()]
        action = {sw: self.timermodevar.get() for sw in switches}
        acttime = time.time() + ((self.hourscale.get() * 60) + self.minutescale.get()) * 60

        self.main.sl.set_timer(acttime, action, self.lockvar.get())
        self.main.set_frame('timers')

    def show(self):
        self.switchbox.delete(0, END)
        [self.switchbox.insert(END, sw) for sw in self.main.sl.get_switches().keys()]
        self.lockvar.set(0)
        self.hourscale.set(0)
        self.minutescale.set(1)
        self.frame.pack(expand = 1, fill = BOTH)

    def hide(self):
        self.frame.pack_forget()

class Main:
    def __init__(self):
        try: self.addr = sys.argv[1].split(':')
        except: print('Usage: switchlight-gui.py server_address[:port]'); quit()
        if len(self.addr) < 2: self.addr.append(25500)

        self.root = Tk()
        self.root.wm_title('Switchlight')
        self.root.geometry('600x360+0+0')
        self.root.after(1, self.loop)

        self.sl = switchlight_api.Client(self.addr[0], int(self.addr[1]))
        self.sl.on_connect = self.on_connect
        self.sl.on_disconnect = self.on_disconnect
        self.sl.on_switches_initialized = self.on_switches_initialized
        self.sl.on_lock = self.on_lock
        self.sl.on_unlock = self.on_unlock

        self.frames = {
                       'message':   MessageFrame(self),
                       'switch':    SwitchFrame(self),
                       'menu':      MenuFrame(self),
                       'lock':      LockFrame(self),
                       'timers':    TimersFrame(self),
                       'settimer':  SetTimerFrame(self)
                      }

        self.frame = self.frames['message']
        self.frame.set_message('Attempting to connect...')
        self.frame.show()

    def set_frame(self, frame):
        self.frame.hide()
        self.frame = self.frames[frame]
        self.frame.show()

    def on_connect(self):
        if not self.sl.get_locked():
            self.set_frame('switch')

    def on_disconnect(self, reason):
        if not reason == switchlight_api.REASON_CLIENT_DISCONNECT:
            self.set_frame('message')
            self.frame.set_message('Disconnected from server: ' + reason)

    def on_switches_initialized(self, switches):
        self.frames['switch'].init_switches(switches)

    def on_lock(self):
        self.set_frame('lock')

    def on_unlock(self):
        self.set_frame('switch')

    def loop(self):
        self.sl.update()
        self.root.after(100, self.loop)

if __name__ == '__main__':
    main = Main()
    try:
        main.root.mainloop()
    except:
        main.sl.disconnect()
        raise
    main.sl.disconnect()
