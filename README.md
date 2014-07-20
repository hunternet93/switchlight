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
    
Using the CLI client:

    python switchlight-cli.py server_address [port] --query
    python switchlight-cli.py server_address [port] --on hallway --off lobby --toggle outsdie
    python switchlight-cli.py server_address [port] --unlock 12345
    python switchlight-cli.py server_address [port] --set-timer 10 --off hallway --off lobby --lock

Switchlight Client API
======================
Programing your own Switchlight program is simple, refer to the clients' code for examples.

Module name: switchlight_api

Starting the client:

    client = switchlight_api.Client(server_address, port)

Functions:

    client.get_connected() -> True or False
    client.get_switches() -> dict
    client.get_timers() -> dict
    client.get_locked() -> True or False
    client.lock() -> None
    client.unlock(passcode) -> True or False
    client.set_timer(time, action, lock) -> None
    client.cancel_timer(timer) -> None
    client.disconnect() -> None

Callbacks:

    client.on_connect                                      Called when the connection to the Switchlight server is (re)established
    client.on_disconnect               str reason          Called when the connection to the Switchlight server is lost
    client.on_switches_initialized     dict switches       Called when switches are initialized
    client.on_switch_toggled           Switch switch       Called when a switch is toggled
    client.on_lock                                         Called when the Switchlight server is locked
    client.on_unlock                                       Called when the Switchlight server is unlocked
    client.on_timer_added              Timer timer         Called when a new Timer is added
    client.on_timer_removed            Timer timer         Called when a Timer is removed, either by cancellation or expiration

Credits
-------
Switchlight was created by Isaac "hunternet93" Smith.

The Switchlight logo was created by rg1024 and published by Openclipart ([link](https://openclipart.org/detail/36265/switch--by-rg1024)). Logo image is in the public domain.
