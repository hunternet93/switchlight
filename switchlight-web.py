#!/usr/bin/env python
import switchlight_api
import time
import sys
import threading
from bottle import run, get, post, request, template, static_file, redirect, response

class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.addr = sys.argv[1].split(':')
        if len(self.addr) < 2: self.addr.append(25500)

        self.sl = switchlight_api.Client(self.addr[0], int(self.addr[1]))
        self.active = True

    def run(self):
        while self.active:
            self.sl.update()
            time.sleep(0.1)

main = None

@get('/')
def webui():
    if main.sl.get_locked(): return template('locked.tpl', incorrect = False)
    return template(
                    'main.tpl',
                    switches = [[s.name, 'on' if s.active else 'off'] for s in main.sl.get_switches().values()], 
                    locked = main.sl.get_locked(),
                    timers = [[time.strftime('%I:%M:%S %p', time.localtime(t.time)),
                               t.action.items(), t.lock, t.id] for t in main.sl.get_timers().values()]
                    )

@get('/set/<switch>')
def set_switch(switch):
    if main.sl.get_locked(): redirect('/'); return
    sw = main.sl.get_switches()[switch]
    sw.set(not sw.active)
    time.sleep(0.2)
    redirect('/')

@get('/lock')
def lock():
    if main.sl.get_locked(): redirect('/'); return
    main.sl.lock()
    time.sleep(0.2)
    redirect('/')

@post('/unlock')
def unlock():
    if main.sl.unlock(request.forms.get('code')):
        time.sleep(0.2)
        redirect('/')
    else:
        return template('locked.tpl', incorrect = True)

@get('/settimer')
def set_timer_page():
    if main.sl.get_locked(): redirect('/'); return
    return template('settimer.tpl', switches = [s.name for s in main.sl.get_switches().values()])

@post('/settimer')
def set_timer():
    if main.sl.get_locked(): redirect('/'); return

    action = {sw: bool(int(request.forms.get('switchmode'))) for sw in request.forms.getall('switches')}
    acttime = time.time() + ((int(request.forms.get('hours')) * 60) + int(request.forms.get('minutes'))) * 60
    main.sl.set_timer(acttime, action, bool(request.forms.get('lock')))
    time.sleep(0.2)
    redirect('/')

@get('/cancel/<id>')
def cancel_timer(id):
    if main.sl.get_locked(): redirect('/'); return
    timer = main.sl.get_timers().get(int(id))
    if timer:
        main.sl.cancel_timer(timer)
        time.sleep(0.2)
    redirect('/')

@get('/logo.svg')
def get_logo():
    response.set_header('Cache-Control', 604800)
    return static_file('switchlight.svg', root='images')

@get('/favicon')
def get_favicon():
    return static_file('switch-small.png', root='images')

try:
    main = Main()
    main.start()
    try: addr = sys.argv[2].split(':')
    except: print('Usage: switchlight-web.py server_address[:port] listen_address[:port]'); quit()
    if len(addr) < 2: addr.append(8080)
    run(host=addr[0], port=int(addr[1]), debug=True)
except:
    main.active = False
    main.sl.disconnect()
    raise
