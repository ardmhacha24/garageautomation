import errno
import os
import logging
from logging.handlers import RotatingFileHandler
import json
from flask import Flask, jsonify
from garageautomation.controller import Controller


def create_root_logger():
    LOGFILE_FORMAT = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)-5s %(message)s [in %(module)s @ %(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    LOGFILE_MODE = 'a'
    LOGFILE_MAXSIZE = 1 * 1024 * 1024
    LOGFILE_BACKUP_COUNT = 10

    # Check whether the specified logs exists or not
    if not os.path.exists(os.path.dirname(app_log_path)):
        try:
            os.makedirs(os.path.dirname(app_log_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Setting up root logging handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(app_log_path,
                                           LOGFILE_MODE,
                                           LOGFILE_MAXSIZE,
                                           LOGFILE_BACKUP_COUNT)
    file_handler.setFormatter(LOGFILE_FORMAT)
    root_logger.addHandler(file_handler)

    return root_logger

app = Flask(__name__)
app_root_dir = os.path.realpath(os.path.dirname(__file__))
app_config_path = os.path.join(app_root_dir, 'config/config.json')
with open(app_config_path) as config_file:
    config = json.load(config_file)
controller = Controller(config, app_root_dir)
#setting up root logger
app_log_path = os.path.join(app_root_dir, controller.config['config']['logs'])
logger = create_root_logger()
logger.info('Loaded default config file from [ %s ] ' % app_config_path)

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

# view history of a door
@app.route("/history/<door_id>", methods=['GET'])
def get_history_door(door_id):
    door_history = controller.get_door_history(door_id)
    return jsonify(door_history)

def run():
    app.run(host='0.0.0.0', port=config['site']['port'], debug=True)

if __name__ == "__main__":
    run()
