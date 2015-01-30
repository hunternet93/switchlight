#!/usr/bin/env python
import switchlight_api
import time
import argparse

parser = argparse.ArgumentParser(prog='switchlight-cli', description='Switchlight CLI Client')
parser.add_argument('server', type=str, help='IP or hostname of the Switchlight server')
parser.add_argument('port', type=str, default='25500', nargs='?', help='Optional port number of Switchlight server') 
parser.add_argument('--query', '-q', action='store_true', help='Queries status of Switchlight server')
parser.add_argument('--toggle', '-t', type=str, nargs=1, action='append', help='Toggles the specified switch')
parser.add_argument('--on', '-o', type=str, nargs=1, action='append', help='Turns the specified switch on')
parser.add_argument('--off', '-f', type=str, nargs=1, action='append', help='Turns the specified switch off')
parser.add_argument('--lock', '-l', action='store_true', help='Locks the Switchlight server')
parser.add_argument('--unlock', '-u', type=str, nargs='?', help='Unlocks the Switchlight server using the specified passcode')
parser.add_argument('--set-timer', '-s', type=int, nargs='?', help='Sets a timer, in minutes, which performs the actions specified on command line')

args = vars(parser.parse_args())

try:
    client = switchlight_api.Client(args['server'], int(args['port']))

    while True:
        time.sleep(0.1)
        client.update()
        if client.get_connected(): break

    if args['set_timer']:
        if args['toggle']:
            print("--toggle cannot be used with --set-timer, use --on or --off instead")
            quit()

        action = {}
        if args['on']:
            for switch in args['on']: action[switch[0]] = client.get_switch(switch[0])).states[-1]
        if args['off']:
            for switch in args['off']: action[switch[0]] = client.get_switch(switch[0])).states[0]
        client.set_timer(time.time() + args['set_timer'] * 60, action, args['lock'])
        print('Timer set.')

    elif args['lock']:
        client.lock()

    elif args['unlock']:
        if client.unlock(args['unlock']):
            print('Switchlight server unlocked successfully.')
        else:
            print('Incorrect passcode.')

    elif args.get('on') or args.get('off') or args.get('toggle'):
        if client.get_locked():
            print('Switchlight server is locked, use --unlock [passcode] to unlock.')
            quit()

        if args['toggle']:
            for s in args['toggle']:
                switch = client.get_switch(s[0])
                if switch.states.index(switch.status) > 0:
                    switch.set(switch.states[0])
                else:
                    switch.set(switch.states[-1])
                    
        if args['on']:
            for s in args['on']:
                switch = client.get_switch(s[0])
                switch.set(switch.states[-1])
        if args['off']:
            for s in args['off']:
                switch = client.get_switch(s[0])
                switch.set(switch.states[0])

    time.sleep(0.25)
    client.update()

    if args['query']:
        switches = client.get_switches()
        for switch in switches.values():
            print(switch.name + ': ' + switch.state)
        for timer in client.get_timers().values():
            print('Timer ' + str(timer.id) + ', ' + time.strftime('%I:%M:%S %p', time.localtime(timer.time)) + ':')
            for a in timer.action.items():
                print('\tSet ' + a[0] + ' ' + a[1])
            if timer.lock: print('\tLock Switchlight')

        locked = 'locked' if client.get_locked() else 'unlocked'
        print('Switchlight is ' + locked)

except:
    client.disconnect()
    raise

client.disconnect()
