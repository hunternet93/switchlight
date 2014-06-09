import sockethandler, time, sys, bottle
from bottle import run, get, template, redirect

bottle.TEMPLATE_PATH=['./']

class Switch:
    def __init__(self, name, num, conn):
        self.name = name
        self.num = num
        self.active = False
        self.conn = conn

    def pressed(self):
        if self.active:
            self.conn.send(['off', self.num])
        else:
            self.conn.send(['on', self.num])

    def on(self):
        self.active = True

    def off(self):
        self.active = False

@get('/')
def webui():
    for msg in conn.recv():
        if msg[0] == 'hi':
            print('connected to server')
            for switch in msg[1:]:
                switches.append(Switch(switch, len(switches), conn))
        if msg[0] == 'sw':
            for i in range(1, len(msg)):
                s = switches[i-1]
                if msg[i] and not s.active:
                    print('switch ' + s.name + ' turned on.')
                    s.on()
                elif not msg[i] and s.active:
                    print('switch ' + s.name + ' turned off.')
                    s.off()

    return template('webui', switches = [[s.name, str(s.num), 'on' if s.active else 'off'] for s in switches])

@get('/set/<switch>')
def set_switch(switch):
    switches[int(switch)].pressed()
    time.sleep(1)
    redirect('/')

conn = sockethandler.client('localhost', 25500)
conn.send(['hi'])
switches = []
run(host='localhost', port=8080, debug=True)
