#!/usr/bin/env python
import sockethandler, yaml, array, sys, time
from ola.ClientWrapper import ClientWrapper

class Switch:
    def __init__(self, name, settings):
        self.name = name
        if settings.get('addr'): self.addrs = [settings['addr']]
        else: self.addrs = settings['addrs']
        self.onval = settings['onval']
        self.offval = settings['offval']
#        self.fade = settings['fade']
        self.fade = 0 # Force fade to 0 because it's broken and I'd like to get on with coding other stuff.
        if settings.get('start'):
            self.active = True
            self.val = self.onval
            self.target = self.onval
        else:
            self.active = False
            self.val = self.offval
            self.target = self.offval

        self.time = None

    def on(self):
        #if self.active: return
        print('switch ' + self.name + ' turned on')
        self.active = True
        if self.fade == 0:
            self.val = self.onval
            self.target = self.onval
        else:
            self.val = self.offval
            self.target = self.onval
        self.time = time.time()

    def off(self):
        if not self.active: return
        print('switch ' + self.name + ' turned off')
        self.active = False
        if self.fade == 0:
            self.val = self.offval
            self.target = self.offval
        else:
            self.val = self.onval
            self.target = self.offval
        self.time = time.time()

    def tick(self):
        # TODO: Fix math below. It doesn't work. At all.
        if self.val < self.target:
            try: t = self.fade / (time.time() - self.time)
            except ZeroDivisionError: t = 0
            self.val = int(((self.onval - self.offval) * t) + self.offval)
            if self.val > self.target: self.val = self.target; print('clamping val to target')

        if self.val > self.target:
            try: t = 1 / (self.fade / (time.time() - self.time))
            except ZeroDivisionError: t = 0
            self.val = int(((self.onval - self.offval) * t) + self.offval)
            if self.val < self.target: self.val = self.target; print('clamping val to target')

        return self.addrs, self.val


class Main:
    def __init__(self):
        self.settings = yaml.load(open('settings.yaml', 'r'))
        self.serv = sockethandler.server(self.settings.get('address') or 'localhost', self.settings.get('port') or 25500)
        self.clients = []

        self.switches = []
        for switch in self.settings['switches'].items():
            self.switches.append(Switch(switch[0], switch[1]))

        self.current_dmx = array.array('B', [0] * 512)

        self.wrapper = ClientWrapper()
        self.wrapper.AddEvent(100, self.loop)

    def loop(self):
        self.wrapper.AddEvent(100, self.loop)
        for msg, addr in self.serv.recv():
            print(msg, addr)
            if not addr in self.clients:
                self.clients.append(addr)
                print('client ' + str(addr) + ' connected')
            if msg[0] == 'hi':
                self.serv.send(['hi'] + [s.name for s in self.switches], addr)
            elif msg[0] == 'on':
                self.switches[msg[1]].on()
            elif msg[0] == 'off':
                self.switches[msg[1]].off()
            elif msg[0] == 'bye':
                print('client ' + str(addr) + ' disconnected')
                self.clients.remove(addr)

        dmx = array.array('B', [0] * 512)
        msg = ['sw']

        for switch in self.switches:
            addrs, val = switch.tick()
            for addr in addrs: dmx[addr] = val
            msg.append(switch.active)

        for client in self.clients:
            self.serv.send(msg, client)
        
        if not dmx == self.current_dmx:
            self.wrapper.Client().SendDmx(self.settings['universe'], dmx, self.DmxSent)
            self.current_dmx = dmx


    def DmxSent(self, state):
        if not state.Succeeded():
            wrapper.Stop()

try:
    main = Main()
    main.wrapper.Run()
except:
    for client in main.clients:
        main.serv.send(['bye'], client)
    main.serv.close()
    raise
