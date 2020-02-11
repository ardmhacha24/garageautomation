import errno
import os
import logging
from logging.handlers import RotatingFileHandler
import re
import RPi.GPIO as gpio
from .door import Door

import time

# import json
# import sys
# import syslog
# import uuid
# import smtplib
# from typing import List

class Controller(object):
    def __init__(self, config, root_dir):
        # setting up the control pins on relay switch
        gpio.setwarnings(False)
        gpio.cleanup()
        gpio.setmode(gpio.BCM)
        # retrieving core config settings
        self.config = config
        self.use_alerts = config['config']['use_alerts']
        self.alert_type = config['alerts']['alert_type']
        self.ttw = config['alerts']['time_to_wait']
        # retrieving door configs from config file
        self.doors = [Door(n, c) for (n, c) in config['doors'].items()]
        # retrieving logs location and setting up
        self.app_root = root_dir
        self.app_log_path = os.path.join(self.app_root, self.config['config']['logs'])
        self.logger = self.create_logger()
        # Log system startup
        self.logger.info('---------- Garage Automation System (GAS) Starting up')
        self.logger.info('__name__ is \'%s\'' % __name__)

    def create_logger(self):
        LOGFILE_FORMAT = '%(asctime)s [%(process)-5d:%(thread)#x] %(name)s %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
        LOGFILE_MODE = 'a'
        LOGFILE_MAXSIZE = 1 * 1024 * 1024
        LOGFILE_BACKUP_COUNT = 10

        # Check whether the specified logs exists or not
        if not os.path.exists(os.path.dirname(self.app_log_path)):
            try:
                os.makedirs(os.path.dirname(self.app_log_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Setting up logging handler
        logger = logging.getLogger('garage_logs')
        logger.setLevel(logging.DEBUG)
        file_handler = RotatingFileHandler(self.app_log_path,
                                           LOGFILE_MODE,
                                           LOGFILE_MAXSIZE,
                                           LOGFILE_BACKUP_COUNT)
        file_handler.setFormatter(logging.Formatter(LOGFILE_FORMAT))
        logger.addHandler(file_handler)

        return logger

    def get_door_status(self, door_id):
        door_status = []
        for d in self.doors:
            if d.id == door_id:
                d.get_state()
                door_status = [
                    {
                        "id": d.id,
                        "name": d.name,
                        "last_state": d.last_state,
                        "last_state_time": d.last_state_time,
                        "last_action": d.last_action,
                        "last_action_time": d.last_action_time,
                        "real_time_state": d.get_state()
                    }
                ]
        if door_status:
            return door_status
        else:
            self.logger.warning('Door Status Request - door id does not exist: [ %s ]' % door_id)
            return ('WARNING: Door Status Request - door id does not exist: [ %s ]' % door_id)

    def get_all_door_status(self):
        door_all_status = [
            {
                "id": d.id,
                "name": d.name,
                "last_state": d.last_state,
                "last_state_time": d.last_state_time,
                "last_action": d.last_action,
                "last_action_time": d.last_action_time,
                "real_time_state": d.get_state()
            }
            for d in self.doors
        ]
        return door_all_status

    def toggle(self, door_id, action_requested):
        self.logger.debug('Received Request to togle door: [ %s:%s ]' %
                             (door_id, action_requested))
        if (action_requested == 'open') or (action_requested == 'close'):
            # logging the action request to build up a door view history
            self.logger.info('Action Requested - request to: [ %s:%s ]' %
                             (door_id, action_requested))
            for d in self.doors:
                if d.id == door_id:
                    action_status = d.toggle_relay(action_requested)
                    if action_status:
                        return action_status
                    else:
                        self.logger.warning('Action Requested - took no action as door already in desired state: [ %s:%s:%s ]' %
                                            (door_id, d.get_state(), action_requested, d.last_action_time))
                        return ('WARNING: Action Requested - took no action as door already in desired state: [ %s:%s:%s ]' %
                                            (door_id, d.get_state(), action_requested, d.last_action_time))
                else:
                    self.logger.warning('Action Requested - door id does not exist: [ %s:%s ]' %
                                        (door_id, action_requested))
                    return ('WARNING: Action Requested - door id does not exist: [ %s:%s ]' %
                            (door_id, action_requested))
        else:
            self.logger.warning('Action Requested - requested action is not supported: [ %s:%s ]' %
                                (door_id, action_requested))
            return ('WARNING: Action Requested - requested action is not supported: [ %s:%s ]' %
                    (door_id, action_requested))

    def get_door_history(self, door_id):
        door_history = []

        log_pattern = re.compile(r"([0-9\-]*)T([0-9\-:.+]*)\s*\[([^]]*)\](.*)")

        with open(self.app_log_path, "r") as f:
            for line in f:
                match = log_pattern.match(line)
                if not match:
                    continue
                grps = match.groups()
                print("Log line:")
                print(f"  date:{grps[0]},\n  time:{grps[1]},\n  type:{grps[2]},\n  text:{grps[3]}")
                door_history = [
                    {
                        "line": line
                    }
                ]