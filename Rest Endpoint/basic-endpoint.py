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
@app.route('/doors/<int:door>', methods=['GET'])
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