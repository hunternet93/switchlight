import sockethandler, threading, time, sys, bottle
from bottle import run, get, post, request, template, redirect

class Switch:
    def __init__(self, name, conn):
        self.name = name
        self.active = False
        self.conn = conn

    def pressed(self):
        if self.active:
            self.conn.send(['off', self.name])
            self.active = False
        else:
            self.conn.send(['on', self.name])
            self.active = True

    def on(self):
        self.active = True

    def off(self):
        self.active = False

class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.conn = sockethandler.client('localhost', 25500)
        self.conn.send(['hi'])
        self.switches = {}

        self.active = True
        self.locked = False
        self.passcode = None
        
    def run(self):
        while self.active:
            for msg in self.conn.recv():
                    if msg[0] == 'hb':
                        self.conn.send(['hb'])

                    if msg[0] == 's':
                        if not [s[0] for s in msg[1]['sw']] == [s.name for s in self.switches.values()]:
                            for sw in self.switches.values(): 
                                del self.switches[sw.name]
                            for m in msg[1]['sw']:
                                self.switches[m[0]] = Switch(m[0], self.conn)

                        for m in msg[1]['sw']:
                            s = self.switches[m[0]]
                            if m[1] and not s.active:
                                print('switch ' + s.name + ' turned on.')
                                s.on()
                            elif not m[1] and s.active:
                                print('switch ' + s.name + ' turned off.')
                                s.off()

                        if not self.passcode: self.passcode = msg[1]['l'][0]
                        self.locked = msg[1]['l'][1]

            time.sleep(0.1)

main = None

@get('/')
def webui():
    return template('webui.tpl', switches = [[s.name, 'on' if s.active else 'off'] for s in main.switches.values()], locked = main.locked)


@get('/set/<switch>')
def set_switch(switch):
    main.switches[switch].pressed()
    redirect('/')

@get('/lock')
def lock():
    main.conn.send(['lock'])
    main.locked = True
    redirect('/')

@post('/unlock')
def unlock():
    if request.forms.get('code') == str(main.passcode):
        main.conn.send(['unlock'])
        main.locked = False
        redirect('/')
    else:
        return "<meta http-equiv='refresh' content='3, url=/'>Incorrect passcode!"


try:
    main = Main()
    main.start()
    run(host='0.0.0.0', port=80, debug=True)
except:
    main.active = False
    conn.close()
    raise
