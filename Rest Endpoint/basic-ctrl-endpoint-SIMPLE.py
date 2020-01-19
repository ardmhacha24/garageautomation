# Software to monitor and control my garage doors via a raspberry pi.

import time, sys, syslog, uuid
import smtplib
import RPi.GPIO as gpio
import json
import httplib
import urllib
import subprocess

class Door(object):
    last_action = None
    last_action_time = None
    msg_sent = False
    pb_iden = None

    def __init__(self, doorId, config):
        self.id = doorId
        self.name = config['name']
        self.relay_pin = config['relay_pin']
        self.state_pin = config['state_pin']
        self.state_pin_closed_value = config.get('state_pin_closed_value', 0)
        self.time_to_close = config.get('time_to_close', 10)
        self.time_to_open = config.get('time_to_open', 10)
        self.open_time = time.time()
        gpio.setup(self.relay_pin, gpio.OUT)
        gpio.setup(self.state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.output(self.relay_pin, True)

    def get_state(self):
        if gpio.input(self.state_pin) == self.state_pin_closed_value:
            return 'closed'
        elif self.last_action == 'open':
            if time.time() - self.last_action_time >= self.time_to_open:
                return 'open'
            else:
                return 'opening'
        elif self.last_action ==  'close':
            if time.time() - self.last_action_time >= self.time_to_close:
                return 'open' # This state indicates a problem
            else:
                return 'closing'
        else:
            return 'open'

    def toggle_relay(self):
        state = self.get_state()
        if (state == 'open'):
            self.last_action = 'close'
            self.last_action_time = time.time()
        elif state == 'closed':
            self.last_action = 'open'
            self.last_action_time = time.time()
        else:
            self.last_action = None
            self.last_action_time = None

        gpio.output(self.relay_pin, False)
        time.sleep(0.2)
        gpio.output(self.relay_pin, True)

class Controller(object):
    def __init__(self, config):
        #setting up flask framework for our endoint
        from flask import Flask, render_template, request, jsonify, abort, url_for
        global app = Flask(__name__)

        #setting up the control pins on relay switch
        gpio.setwarnings(False)
        gpio.cleanup()
        gpio.setmode(gpio.BCM)
        self.config = config
        self.doors = [Door(n, c) for (n, c) in config['doors'].items()]
        ##self.updateHandler = UpdateHandler(self)
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
                #self.updateHandler.handle_updates()

            if new_state == 'open' and not door.msg_sent and time.time() - door.open_time >= self.ttw:
                if self.use_alerts:
                    title = "%s's garage door open" % door.name
                    etime = elapsed_time(int(time.time() - door.open_time))
                    message = "%s's garage door has been open for %s" % (door.name, etime)
                    door.msg_sent = True

            if new_state == 'closed':
                if self.use_alerts:
                    if door.msg_sent == True:
                        title = "%s's garage doors closed" % door.name
                        etime = elapsed_time(int(time.time() - door.open_time))
                        message = "%s's garage door is now closed after %s  "% (door.name, etime)
                door.open_time = time.time()
                door.msg_sent = False

    def toggle(self, doorId):
        for d in self.doors:
            if d.id == doorId:
                syslog.syslog('%s: toggled' % d.name)
                d.toggle_relay()
                return

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
    def get_doors():
        return jsonify({'doors': doors})
        # return jsonify({'doors': [make_public_door(door) for door in doors]})

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