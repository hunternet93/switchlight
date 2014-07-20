![](images/switchlight.png)
===========

Switchlight is a simple OpenLightingArchitecture network light switch designed to turn lights on and off while the primary DMX controller is offline. It supports multiple clients using a native client or a web UI.

Requirements
------------
Server: Python, [OLA](http://www.openlighting.org/ola), YAML

CLI Client: Python

GUI Client: Python, Tkinter

Web Client: Python, Bottle

Usage
-----
The server settings are defined in settings.yaml, see the included settings.yaml.example for syntax.

To start the server, simply run:

    python switchlight-server.py

To start the web server:

    python swithlight-web.py server_address[:port] listen_address[:port]

To start the GUI client:

    python switchlight-gui.py server_address[:port]


Switchlight Client API
======================
Programing your own Switchlight program is simple, refer to the clients' code for examples.

Module name: switchlight_api

Functions:

    get_connected() -> True or False
    get_switches() -> dict
    get_timers() -> dict
    get_locked() -> True or False
    lock() -> None
    unlock(passcode) -> True or False
    set_timer(time, action, lock) -> None
    cancel_timer(timer) -> None
    disconnect() -> None

Callbacks:

    on_connect                                      Called when the connection to the Switchlight server is (re)established
    on_disconnect               str reason          Called when the connection to the Switchlight server is lost
    on_switches_initialized     dict switches       Called when switches are initialized
    on_switch_toggled           Switch switch       Called when a switch is toggled
    on_lock                                         Called when the Switchlight server is locked
    on_unlock                                       Called when the Switchlight server is unlocked
    on_timer_added              Timer timer         Called when a new Timer is added
    on_timer_removed            Timer timer         Called when a Timer is removed, either by cancellation or expiration

Credits
-------
Switchlight was created by Isaac "hunternet93" Smith.

The Switchlight logo was created by rg1024 and published by Openclipart ([link](https://openclipart.org/detail/36265/switch--by-rg1024)). Logo image is in the public domain.
