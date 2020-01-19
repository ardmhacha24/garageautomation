# Testing flask as api endpoint

import time
import sys

from flask import Flask, render_template, request, jsonify, abort, url_for
#app = Flask(__name__, static_url_path='/static')

app = Flask(__name__)
doors = [
    {
        'id' : 'left',
        'name' : 'Left Door',
        'openpin' : 12,
        'closepin' : 16,
        'state' : 'closed'
    },
    {
        'id' : 'right',
        'name' : 'Right Door',
        'openpin' : 20,
        'closepin' : 21,
        'state' : 'closed'
    }
]

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



def make_public_door(door):
    new_door = {}
    for field in door:
        if field == 'id':
            new_door['uri'] = url_for('get_door', door_id=door['id'], _external=True)
        else:
            new_door[field] = door[field]
    return new_door

@app.route('/')
def index():
    return "Hello, World!"

# check all door status endpoint
@app.route('/doors', methods=['GET'])
def get_doors():
    return jsonify({'doors': doors})
    #return jsonify({'doors': [make_public_door(door) for door in doors]})

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
   return "Lets do somethimg with ths door.. %s:%s" % (door,action)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)