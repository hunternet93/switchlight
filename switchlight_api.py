"""Switchlight client API

This module provides the API for client applications to interact with a
Switchlight server."""

import sockethandler
import time

REASON_TIMEOUT = 'REASON_TIMEOUT'
REASON_SERVER_DISCONNECT = 'REASON_SERVER_EXIT'
REASON_CLIENT_DISCONNECT = 'REASON_CLIENT_DISCONNECT'

class Switch:
    def __init__(self, name, states, status, conn):
        self.name = name
        self.states = states
        self.status = status
        self._conn = conn
        
        self.changed = lambda: None

    def set(self, statename):
        self._conn.send(['set', self.name, statename])

class Timer:
    def __init__(self, id, time, action, lock):
        self.id = id 
        self.time = time
        self.action = action
        self.lock = lock


class Client:
    """Create a Switchlight Client object

    The Client initiates a connection to the Switchlight server and provides
    an API for client applications to interact with the server.
    """
    def __init__(self, server, port):
        # Creates the connection to the server
        self._conn = sockethandler.client(server, port)
        self._conn.send(['hi'])
        self._connected = False
        self._lasthb = None

        self._switches = {}
        self._timers = {}
        self._locked = False
        self._passcode = None

        self.on_connect = \
            self.on_disconnect = \
            self.on_switches_initialized = \
            self.on_switch_changed = \
            self.on_lock = \
            self.on_unlock = \
            self.on_timer_added = \
            self.on_timer_removed = \
            lambda *x: None

    def _on_connect(self):
        # Called when the connection to the Switchlight server is (re)established.
        self._connected = True
        self.on_connect()

    def _on_disconnect(self, reason):
        # Called when the connection to the Switchlight server is lost.
        self._connected = False
        self.on_disconnect(reason)

    def _initialize_switches(self, msg):
        # Called to initialize switches
        for sw in msg: self._switches[sw['name']] = Switch(sw['name'], sw['states'], sw['status'], self._conn)
        self.on_switches_initialized(self._switches)

    def _on_switch_changed(self, switch, status):
        # Called when a switch is changed\
        switch.status = status
        switch.changed()
        self.on_switch_changed(switch, status)

    def _on_lock(self):
        # Called when Switchlight server is locked
        self._locked = True
        self.on_lock()

    def _on_unlock(self):
        # Called when Switchlight server is unlocked
        self._locked = False
        self.on_unlock()

    def _on_timer_added(self, timer):
        # Called when a Timer is added
        self._timers[timer[0]] = Timer(*timer)
        self.on_timer_added(self._timers[timer[0]])

    def _on_timer_removed(self, timer):
        # Called when a Timer is removed
        del self._timers[timer.id]
        self.on_timer_removed(timer)

    def get_connected(self):
        """Returns True if the connection to the Switchlight server is active, False otherwise"""
        return self._connected

    def get_switches(self):
        """Returns dictionary of switches indexed by name"""
        return self._switches

    def get_switch(self, switch):
        """Get Switch by name, or None if no switch has that name"""
        return self._switches.get(switch)

    def get_timers(self):
        """Returns a dictionary of timers indexed by ID"""
        return self._timers

    def get_locked(self):
        """Returns True if Switchlight is locked, False otherwise"""
        return self._locked

    def lock(self):
        """Locks the Switchlight server"""
        self._conn.send(['lock'])

    def unlock(self, passcode):
        """Unlocks the Switchlight server if passcode string is correct

        Returns True if successful, False if passcode is incorrect"""
        if str(passcode) == str(self._passcode):
            self._conn.send(['unlock'])
            return True

        else: return False

    def set_timer(self, time, action, lock):
        """Sets a timer

        time is the target time in seconds since the UNIX epoch
        action is a dict of switch names and boolean values, i.e. {'Hallway': False}
        lock is whether to lock Switchlight after the timer expires, True or False
        """
        self._conn.send(['timer', time, action, lock])

    def cancel_timer(self, timer):
        """Cancels a timer"""
        self._conn.send(['cancel_timer', timer.id])

    def disconnect(self):
        self._conn.send(['bye'])
        self._conn.close()
        self._on_disconnect(REASON_CLIENT_DISCONNECT)

    def update(self):
        """Handles communication with the Switchlight server

        Update must be called at least once per second to prevent disconnection
        """
        if self._connected and self._lasthb > time.time() + 1.5:
            self._on_disconnect(REASON_TIMEOUT)

        for msg in self._conn.recv():
            if msg[0] == 'hb':
                if not self._connected: self._on_connect()
                self._lasthb = time.time()
                self._conn.send(['hb'])

            elif msg[0] == 's':
                if not len(self._switches): self._initialize_switches(msg[1]['sw'])

                for sw in msg[1]['sw']:
                    if not self._switches[sw['name']].status == sw['status']:
                        self._on_switch_changed(self._switches[sw['name']], sw['status'])

                for t in msg[1]['t']:
                    if not self._timers.get(t[0]): self._on_timer_added(t)

                for timer in list(self._timers.values()):
                    if not timer.id in [t[0] for t in msg[1]['t']]:
                        self._on_timer_removed(timer)

                if not self._passcode: self._passcode = msg[1]['l'][0]
                if msg[1]['l'][1] == True and not self._locked: self._on_lock()
                if msg[1]['l'][1] == False and self._locked: self._on_unlock()

            elif msg[0] == 'bye':
                self._on_disconnect(REASON_SERVER_EXIT)
