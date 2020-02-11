import os
import logging
import re
import RPi.GPIO as gpio
from .door import Door


class Controller(object):
    def __init__(self, config, app_root_dir):
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
        self.app_log_path = os.path.join(app_root_dir, self.config['config']['logs'])
        self.logger = logging.getLogger(__name__)
        # Log controller startup
        self.logger.debug('------ GAS: Controller initialised')
        self.logger.debug('------ GAS: Doors loaded : [%s]' % self.doors)

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
        self.logger.debug('Received Request to toggle door: [ %s:%s ]' %
                             (door_id, action_requested))
        if (action_requested == 'open') or (action_requested == 'close'):
            for d in self.doors:
                if d.id == door_id:
                    action_status = d.toggle_relay(action_requested)
                    if action_status:
                        # logging the action request to build up a door view history
                        self.logger.info('Action Requested - request to: [ %s:%s ]' %
                                         (door_id, action_requested))
                        self.logger.info(action_status)
                        return action_status
                    else:
                        self.logger.warning('Action Requested - took no action as door already in desired state: [ %s:%s:%s:%s ]' %
                                            (door_id, d.get_state(), action_requested, d.last_action_time))
                        return ('WARNING: Action Requested - took no action as door already in desired state: [ %s:%s:%s:%s ]' %
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