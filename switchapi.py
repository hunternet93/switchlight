"""Switchlight client API

This module provides the API for client applications to interact with a
Switchlight server."""

import sockethandler
import time

REASON_TIMEOUT = 'REASON_TIMEOUT'
REASON_SERVER_DISCONNECT = 'REASON_SERVER_EXIT'
REASON_CLIENT_DISCONNECT = 'REASON_CLIENT_DISCONNECT'

class Switch:
    def __init__(self, name, active, conn):
        self.name = name
        self.active = active
        self._conn = conn

    def set(self, state):
        if state == self.active: return
        if self.active:
            self._conn.send(['off', self.name])
            self.active = False
        else:
            self._conn.send(['on', self.name])
            self.active = True

    def on(self):
        self.active = True

    def off(self):
        self.active = False


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

    def _on_connect(self):
        # Called when the connection to the Switchlight server is (re)established.
        self._connected = True
        self.on_connect()

    def on_connect(self):
        """Called when the connection to the Switchlight server is (re)established

        on_connect does nothing by default but may be overriden by client applications.
        """
        pass

    def _on_disconnect(self, reason):
        # Called when the connection to the Switchlight server is lost.
        self._connected = False
        self.on_disconnect(reason)

    def on_disconnect(self, reason):
        """Called when the connection to the Switchlight server is lost

        on_disconnect does nothing by default but may be overriden by client applications.
        on_disconnect is passed a reason constant that describes why the
        disconnection occurred, which can be one of:
            REASON_TIMEOUT           - The connection to the server timed out
            REASON_SERVER_DISCONNECT - The server closed the connection
            REASON_CLIENT_DISCONNECT - The client closed the connection
        """
        pass

    def _initialize_switches(self, msg):
        # Called to initialize switches
        for sw in msg: self._switches[sw[0]] = Switch(sw[0], sw[1], self._conn)
        self.on_switches_initialized(self._switches)

    def on_switches_initialized(self, switches):
        """Called when switches are initialized

        Does nothing by default but may be overriden by client applications.
        on_switches_initialized is passed with a dictionary of Switch objects, indexed by name
        """
        pass

    def _on_switch_toggled(self, switch):
        # Called when a switch is toggled
        if switch.active: switch.off()
        else: switch.on()
        self.on_switch_toggled(switch)

    def on_switch_toggled(self, switch):
        """Called when a switch is toggled


        on_switch_toggled does nothing by default but may be overriden by client applicaitons.
        on_switch_toggled is passed the Switch object of the toggled switch
        """
        pass

    def _on_lock(self):
        # Called when Switchlight server is locked
        self.locked = True
        self.on_lock()

    def on_lock(self):
        """Called when the Switchlight server is locked

        on_lock does nothing by default but may be overriden by client applicaitons.
        """
        pass

    def _on_unlock(self):
        # Called when Switchlight server is unlocked
        self.locked = False
        self.on_unlock()

    def on_unlock(self):
        """Called when the Switchlight server is unlocked

        on_unlock does nothing by default but may be overriden by client applicaitons.
        """
        pass

    def _on_timer_added(self, timer):
        # Called when a Timer is added
        self._timers[timer[0]] = Timer(*timer)
        self.on_timer_added(self._timers[timer[0]])

    def on_timer_added(self, timer):
        """Called when a new Timer is added

        on_timer_added nothing by default but may be overriden by client applicaitons.
        on_timer_added is passed the new Timer object.
        """
        pass

    def _on_timer_removed(self, timer):
        # Called when a Timer is removed
        del self._timers[timer.id]
        self.on_timer_removed(timer)

    def on_timer_removed(self, timer):
        """Called when a Timer is removed, either by cancellation or expiration

        on_timer_removed nothing by default but may be overriden by client applicaitons.
        on_timer_removed is passed the removed Timer object.
        """
        pass

    def get_connected(self):
        """Returns True if the connection to the Switchlight server is active, False otherwise"""
        return self._connected

    def get_switches(self):
        """Returns dictionary of switches indexed by name"""
        return self._switches

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
        if passcode == self._passcode:
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

    def cancel_timer(self, id):
        """Cancels a timer by ID"""
        self._conn.send(['cancel_timer', id])

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
                    if not self._switches[sw[0]].active == sw[1]:
                        self._on_switch_toggled(self._switches[sw[0]])

                for t in msg[1]['t']:
                    if not self._timers.get(t[0]): self._on_timer_added(t)

                for timer in self._timers.values():
                    if not timer.id in [t[0] for t in msg[1]['t']]:
                        self._on_timer_removed(timer)

                if not self._passcode: self._passcode = msg[1]['l'][0]
                if msg[1]['l'][1] == True and not self._locked: self.on_lock()
                if msg[1]['l'][1] == False and self._locked: self.on_unlock()

            elif msg[0] == 'bye':
                self._on_disconnect(REASON_SERVER_EXIT)
