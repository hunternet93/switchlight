#!/usr/bin/env python
import sockethandler
import yaml
import array
import sys
import time
import random
import collections
from ola.ClientWrapper import ClientWrapper

class Switch:
    def __init__(self, name, settings, defaults):
        self.name = name
        if settings.get('addr'):
            self.addrs = [settings['addr']]
        else:
            self.addrs = settings['addrs']

        if settings.get('states'):
            self.statenames = []
            self.states = []
            
            for s in settings.get('states'):
                self.statenames.append(s.keys()[0])
                self.states.append(s.values()[0])
        
        else:
            self.statenames = ['off', 'on']
            self.states = [0, settings.get('on') or 255]

        self.fade = settings.get('fade') or defaults.get('fade') or 0
        self.universe = settings.get('universe') or defaults.get('universe')

        if settings.get('start'):
            self.status = self.statenames.index(settings['start'])
        else:
            self.status = 0

        self.target = self.states[self.status]
        self.val = self.states[self.status]
        self.time = None
        
    def json(self):
        return {
            'name': self.name,
            'states': self.statenames,
            'status', self.status
        }

    def set(self, statename):
        print('switch ' + self.name + ' set to ' + statename)
        try:
            self.status = self.statenames.index(statename)
        except ValueError:
            print('invalid state name: ' + statename)
            
        self.target = self.states[self.status]
        self.time = time.time()

    def tick(self):
        if self.val < self.target:
            try: self.val = int(self.target / (self.fade / (time.time() - self.time)))
            except ZeroDivisionError: self.val = self.target
            if self.val > self.target: self.val = self.target

        if self.val > self.target:
            try: self.val = int(self.onval / (self.fade / (self.fade - (time.time() - self.time))))
            except ZeroDivisionError: self.val = self.target
            if self.val < self.target: self.val = self.target

        return self.addrs, self.val


class Timer:
    def __init__(self, time, action, lock, main):
        self.time = time
        self.action = action
        self.lock = lock
        self.id = random.randint(1, 9999)
        self.main = main

    def check(self):
        if self.time <= time.time():
            for s in self.action.items():
                switch = self.main.switches.get(s[0])
                switch.set(s[1])

            if self.lock:
                self.main.locked = True

            return True

        else:
            return False

class Client:
    def __init__(self, addr):
        self.addr = addr
        self.lasthb = time.time()

class Main:
    def __init__(self):
        self.settings = yaml.load(open('settings.yaml', 'r'))
        self.serv = sockethandler.server(self.settings.get('address') or 'localhost', self.settings.get('port') or 25500)
        self.clients = {}
        self.timers = {}

        self.locked = False
        self.passcode = self.settings['passcode']

        self.defaults = self.settings['defaults']

        self.universes = {}
        self.switches = {}
        for s in self.settings['switches'].items():
            switch = Switch(s[0], s[1], self.defaults)
            if not self.universes.get(switch.universe):
                self.universes[switch.universe] = array.array('B', [0] * 512)
                
            self.switches[s[0]] = switch

        self.wrapper = ClientWrapper()
        self.wrapper.AddEvent(100, self.loop)

    def send_status(self, clients):
        status = {}
        status['sw'] = [s.json() for s in self.switches.values()]
        status['l'] = [self.passcode, self.locked]
        status['t'] = [[t.id, t.time, t.action, t.lock] for t in self.timers.values()]
        for client in clients:
            self.serv.send(['s', status], client.addr)

    def loop(self):
        self.wrapper.AddEvent(100, self.loop)
        send_update = False
        for msg, addr in self.serv.recv():
            if self.settings.get('debug'): print(msg, addr)
            if not self.clients.get(addr):
                self.clients[addr] = Client(addr)
                print('client ' + str(addr) + ' connected')

            client = self.clients[addr]

            if msg[0] == 'hi':
                self.send_status([client])

            if msg[0] == 'hb':
                client.lasthb = time.time()
                
            elif msg[0] == 'set':
                if self.locked: self.send_status([client])
                else:
                    self.switches[msg[1]].set(msg[2])
                    send_update = True
                    
            elif msg[0] == 'lock':
                print('locked by client: ', client.addr)
                self.locked = True
                send_update = True

            elif msg[0] == 'unlock':
                print('unlocked by client: ', client.addr)
                self.locked = False
                send_update = True

            elif msg[0] == 'timer':
                print('timer set:', msg[1:])
                timer = Timer(msg[1], msg[2], msg[3], self)
                self.timers[timer.id] = timer
                send_update = True

            elif msg[0] == 'cancel_timer':
                print('timer canceled:', msg[1:])
                try: del self.timers[msg[1]]
                except KeyError: pass
                send_update = True

            elif msg[0] == 'bye':
                print('client ' + str(addr) + ' disconnected')
                del self.clients[addr]

        curr_universes = {u[0]: array.array('B', u[1]) for u in self.universes.items()}
        msg = ['sw']

        for switch in self.switches.values():
            addrs, val = switch.tick()
            for addr in addrs:
                curr_universes[switch.universe][addr-1] = val

        for timer in self.timers.values():
            if timer.check():
                del self.timers[timer.id]
                send_update = True

        for client in self.clients.values():
            if time.time() - client.lasthb > 0.5:
                self.serv.send(['hb'], client.addr)

            if time.time() - client.lasthb > 2:
                print('client ' + str(client.addr) + ' timed out')
                del self.clients[client.addr]

        if not curr_universes == self.universes:
            send_update = True
            for universe in curr_universes.items():
                self.wrapper.Client().SendDmx(universe[0], universe[1], self.DmxSent)
            self.universes = curr_universes

        if send_update:
            self.send_status(self.clients.values())

    def DmxSent(self, state):
        if not state.Succeeded():
            wrapper.Stop()


main = Main()
try:
    main.wrapper.Run()
except:
    for client in main.clients.values():
        main.serv.send(['bye'], client.addr)
    main.serv.close()
    raise
