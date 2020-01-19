# Software to monitor and control my garage doors via a raspberry pi.

import time, sys, syslog, uuid
import smtplib
import RPi.GPIO as gpio
import json
import httplib
import urllib
import subprocess

#setting up flask framework for our endoint
from flask import Flask, render_template, request, jsonify, abort, url_for
global app = Flask(__name__)

class Door(object):
    last_action = None
    last_action_time = None

    def __init__(self, doorId, config):
        self.id = doorId
        self.name = config['name']
        self.open_pin = config['open_pin']
        self.close_pin = config['close_pin']
        self.closed_state_pin = config['closed_state_pin']
        self.opened_state_pin = config['opened_state_pin']
        self.pin_closed_value = config.get('pin_closed_value', 0)
        self.time_to_openclose = config.get('approx_time_to_openclose', 10)
        self.open_time = time.time()
        #initiatting open/close pins
        gpio.setup(self.open_pin, gpio.OUT)
        gpio.output(self.open_pin, True)
        gpio.setup(self.close_pin, gpio.OUT)
        gpio.output(self.close_pin, True)
        #initiating door status reed switches
        gpio.setup(self.closed_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.opened_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

    def get_state(self):
        if gpio.input(self.closed_state_pin) == self.pin_closed_value:
            return 'closed'
        elif self.last_action == 'open':
            if gpio.input(self.opened_state_pin) == self.pin_closed_value:
                return 'opened'
            elif (time.time() - self.last_action_time >= self.time_to_openclose) and (gpio.input(self.opened_state_pin) != self.pin_closed_value) and (gpio.input(self.closed_state_pin) != self.pin_closed_value):
                return 'opening error - taking too long'
            else:
                return 'opening'
        elif self.last_action ==  'close':
            if gpio.input(self.closed_state_pin) == self.pin_closed_value:
                return 'closed'
            elif (time.time() - self.last_action_time >= self.time_to_openclose) and (gpio.input(self.closed_state_pin) != self.pin_closed_value) and (gpio.input(self.opened_state_pin) != self.pin_closed_value):
                return 'closing error - taking too long'
            else:
                return 'closing'
        else:
            return 'opened'

    def toggle_relay(self, action):
        state = self.get_state()
        if (action == 'open') and (state == 'closed'):
            self.last_action = 'open'
            self.last_action_time = time.time()
            gpio.output(self.open_pin, False)
            time.sleep(0.2)
            gpio.output(self.open_pin, True)
        elif (action == 'close') and (state == 'opened'):
            self.last_action = 'close'
            self.last_action_time = time.time()
            gpio.output(self.close_pin, False)
            time.sleep(0.2)
            gpio.output(self.close_pin, True)
        elif (state == 'opening') or (state == 'closing'):
            print('Took no action - already moving... %s:%s:%s', (state, self.last_action,self.last_action_time))
        elif (state == 'opening error - taking too long') or (state == 'closing error - taking too long'):
            print('ERROR - investigate as taking too long... %s:%s:%s', (state, self.last_action,self.last_action_time))
        else:
            self.last_action = None
            self.last_action_time = None

class Controller(object):
    def __init__(self, config):
        #setting up the control pins on relay switch
        gpio.setwarnings(False)
        gpio.cleanup()
        gpio.setmode(gpio.BCM)
        self.config = config
        self.doors = [Door(n, c) for (n, c) in config['doors'].items()]
        for door in self.doors:
            door.last_state = 'unknown'
            door.last_state_time = time.time()

        self.use_alerts = config['config']['use_alerts']
        self.alert_type = config['alerts']['alert_type']
        self.ttw = config['alerts']['time_to_wait']

    def status_check(self):
        for door in self.doors:
            new_state = door.get_state()
            if (door.last_state != new_state):
                syslog.syslog('%s: %s => %s' % (door.name, door.last_state, new_state))
                door.last_state = new_state
                door.last_state_time = time.time()

            if new_state == 'open' and not door.msg_sent and time.time() - door.open_time >= self.ttw:
                if self.use_alerts:
                    title = "%s's garage door open" % door.name
                    etime = elapsed_time(int(time.time() - door.open_time))
                    message = "%s's garage door has been open for %s" % (door.name, etime)

            if new_state == 'closed':
                if self.use_alerts:
                    if door.msg_sent == True:
                        title = "%s's garage doors closed" % door.name
                        etime = elapsed_time(int(time.time() - door.open_time))
                        message = "%s's garage door is now closed after %s  "% (door.name, etime)
                door.open_time = time.time()

    def toggle(self, doorId, action=None):
        for d in self.doors:
            if d.id == doorId:
                syslog.syslog('%s: toggled' % d.name)
                d.toggle_relay(action)

    def get_updates(self, lastupdate):
        updates = []
        for d in self.doors:
            if d.last_state_time >= lastupdate:
                updates.append((d.id, d.last_state, d.last_state_time))
        return updates

    @app.route('/')
    def index():
        return "Hello, World!"

    # check all door status endpoint
    @app.route('/doors', methods=['GET'])
    def get_doors_allstatus():
        for d in self.doors:
            door_allstat = {
                d.id : { d.name, d.last_state, d.last_state_time }
            }
        return jsonify(door_allstat)

    # check individual door status endpoint
    @app.route('/doors/<door>', methods=['GET'])
    def get_door_status(door):
        door = [door for door in doors if door['id'] == door]
        if len(door) == 0:
            abort(404)
        return jsonify({'door': door[0]})

    # do something with our door
    @app.route("/<door>/<action>", methods=['POST'])
    def action(door, action):
        return "Lets do somethimg with ths door.. %s:%s" % (door, action)

    def run(self):
        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=self.config['site']['port'], debug=True)

# main loop
try:

    while True:
        if __name__ == '__main__':
            syslog.openlog('garage_controller')
            config_file = open('sysconfig.json')
            controller = Controller(json.load(config_file))
            config_file.close()
            controller.run()

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quitting...")
    # Reset GPIO settings
    gpio.cleanup()
    sys.exit(0)