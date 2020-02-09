import errno
import time
import logging
from logging.handlers import RotatingFileHandler
import os
# import sys
import syslog
# import uuid
# import smtplib
from typing import List

import RPi.GPIO as gpio
# import json
from .door import Door


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
        print ("hkjjjkhkhkjhkh", self.config['config']['logs'], "ghgjghjhgyuyuu0000")
        self.app_root = root_dir
        self.logger = self.create_logger()
        self.logger.info('garage automation system started up')

    def create_logger(self):
        LOGFILE_FORMAT = '%(asctime)s [%(process)-5d:%(thread)#x] %(name)s %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
        LOGFILE_MODE = 'a'
        LOGFILE_MAXSIZE = 1 * 1024 * 1024
        LOGFILE_BACKUP_COUNT = 10

        # Check whether the specified logs exists or not
        if not os.path.exists(os.path.dirname(os.join(self.app_root, self.config['config']['logs']))):
            try:
                os.makedirs(os.path.dirname(self.config['config']['logs']))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Set up logging
        logger = logging.getLogger('garage_logs')
        logger.setLevel(logging.DEBUG)
        log_path = self.config['config']['logs']

        file_handler = RotatingFileHandler(log_path,
                                           LOGFILE_MODE, \
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
            return ('ERROR: Requested Door ID: [%s] does not exist...',
                    door_id)

    def get_all_door_status(self):
        door_all_status = [
            {
                "id": d.id,
                "name": d.name,
                "last_state": d.last_state,
                "last_state_time": d.last_state_time,
                "last_action": d.last_action,
                "last_actioon_time": d.last_action_time,
                "real_time_state": d.get_state()
            }
            for d in self.doors
        ]
        return door_all_status

    def toggle(self, door_id, action_requested):
        if (action_requested == 'open') or (action_requested == 'close'):
            # logging the action request to build up a door view history
            self.logger.info('Action requested on door %s:%s',door_id, action_requested)
            for d in self.doors:
                if d.id == door_id:
                    action_status = d.toggle_relay(action_requested)
                    if action_status:
                        return action_status
                    else:
                        return ('INFO: Requested action not took - door already in desired state: %s:%s:%s',
                                (door_id, d.get_state(),action_requested,d.last_action_time))
                else:
                    return ('ERROR: Requested Door ID: [%s] does not exist...',
                            door_id)
        else:
            return ('ERROR: Requested Action:[%s] is not supported... [open | close]',
                    action_requested)

    # def status_check(self):
    #     for door in self.doors:
    #         new_state = door.get_state()
    #         if (door.last_state != new_state):
    #             syslog.syslog('%s: %s => %s' % (door.name, door.last_state, new_state))
    #             door.last_state = new_state
    #             door.last_state_time = time.time()

    #         if new_state == 'open' and not door.msg_sent and time.time() - door.open_time >= self.ttw:
    #             if self.use_alerts:
    #                 title = "%s's garage door open" % door.name
    #                 etime = elapsed_time(int(time.time() - door.open_time))
    #                 message = "%s's garage door has been open for %s" % (door.name, etime)

    #         if new_state == 'closed':
    #             if self.use_alerts:
    #                 if door.msg_sent == True:
    #                     title = "%s's garage doors closed" % door.name
    #                     etime = elapsed_time(int(time.time() - door.open_time))
    #                     message = "%s's garage door is now closed after %s  "% (door.name, etime)
    #             door.open_time = time.time()

    # def get_updates(self, lastupdate):
    #     updates = []
    #     for d in self.doors:
    #         if d.last_state_time >= lastupdate:
    #             updates.append((d.id, d.last_state, d.last_state_time))
    #     return updates
