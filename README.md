switchlight
===========

Switchlight is a simple OpenLightingArchitecture network light switch designed to turn lights on and off while the primary DMX controller is offline. It supports multiple clients using a native client or a web UI.

Requirements
------------
Server:     Python, [OLA](http://www.openlighting.org/ola), Python-YAML

Client:     Python, Python-Tkinter

Web Client: Python, Python-Bottle

Usage
-----
The server settings are defined in settings.yaml, see the included settings.yaml.example for syntax.

To start the server, simply run:

    python server.py

To start the web server:

    python webui.py

To start the client:

    python client.py server_address[:port]

Future Features
---------------
Passcode-protected locking capability

Lights-off timer

Credits
-------
Switchlight was created by Isaac "hunternet93" Smith.
