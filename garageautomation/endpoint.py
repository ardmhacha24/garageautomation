# setting up flask framework for our endoint
import json
from flask import Flask, jsonify
from garageautomation.controller import Controller


app = Flask(__name__)

with open('./config/config.json') as config_file:
    config = json.load(config_file)
controller = Controller(config)

@app.route('/')
def index():
    return "Hello, World!"

# check all door status endpoint
@app.route('/doors', methods=['GET'])
def get_doors_all_status():
    all_status = controller.get_all_door_status()
    return jsonify(all_status)

# check individual door status endpoint
@app.route('/doors/<door>', methods=['GET'])
def get_door_status(door):
    status = controller.get_door_status(door)
    return jsonify(status)

# do something with our door endpoint
@app.route("/action/<door>/<action>", methods=['POST'])
def action(door, action):
    return "Lets do somethimg with ths door.. %s:%s" % (door, action)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config['site']['port'], debug=True)
