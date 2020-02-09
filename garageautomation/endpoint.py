#!/usr/bin/env python3
# setting up flask framework for our endoint
import json
from flask import Flask, jsonify
from garageautomation.controller import Controller
from os import path as osp


app = Flask(__name__)
root_dir = osp.realpath(osp.dirname(__file__))
with open(osp.join(root_dir, 'config/config.json')) as config_file:
    config = json.load(config_file)
controller = Controller(config, root_dir)


@app.route('/')
def index():
    return "Nothing to see here..."

# check all door status endpoint
@app.route('/doors', methods=['GET'])
def get_doors_all_status():
    all_status = controller.get_all_door_status()
    return jsonify(all_status)

# check individual door status endpoint
@app.route('/doors/<door_id>', methods=['GET'])
def get_door_status(door_id):
    door_status = controller.get_door_status(door_id)
    return jsonify(door_status)

# do something with our door endpoint
@app.route("/action/<door_id>/<action>", methods=['POST'])
def action_door(door_id, action):
    action_status = controller.toggle(door_id, action)
    return jsonify(action_status)

def run():
    app.run(host='0.0.0.0', port=config['site']['port'], debug=True)

if __name__ == "__main__":
    run()
