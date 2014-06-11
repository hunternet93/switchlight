import sockethandler, threading, time, sys, bottle
from bottle import run, get, template, redirect

class Switch:
    def __init__(self, name, conn):
        self.name = name
        self.active = False
        self.conn = conn

    def pressed(self):
        if self.active:
            self.conn.send(['off', self.name])
        else:
            self.conn.send(['on', self.name])

    def on(self):
        self.active = True

    def off(self):
        self.active = False

class SwThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.active = True
        
    def run(self):
        while self.active:
            for msg in conn.recv():
                    if msg[0] == 'hb':
                        conn.send(['hb'])

                    if msg[0] == 's':
                        if not [s[0] for s in msg[1]['sw']] == [s.name for s in switches.values()]:
                            for sw in switches.values(): 
                                del switches[sw.name]
                            for m in msg[1]['sw']:
                                switches[m[0]] = Switch(m[0], conn)

                        for m in msg[1]['sw']:
                            s = switches[m[0]]
                            if m[1] and not s.active:
                                print('switch ' + s.name + ' turned on.')
                                s.on()
                            elif not m[1] and s.active:
                                print('switch ' + s.name + ' turned off.')
                                s.off()

            time.sleep(0.1)


@get('/')
def webui():
    return template('webui.tpl', switches = [[s.name, 'on' if s.active else 'off'] for s in switches.values()])


@get('/set/<switch>')
def set_switch(switch):
    switches[switch].pressed()
    time.sleep(1)
    redirect('/')

conn = sockethandler.client('localhost', 25500)
conn.send(['hi'])
switches = {}
try:
    st = SwThread()
    st.start()
    run(host='localhost', port=8080, debug=True)
except:
    st.active = False
    conn.close()
    raise
