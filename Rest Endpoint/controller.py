import time
# import sys
import syslog
# import uuid
# import smtplib
import RPi.GPIO as gpio
# import json
from .door import Door


class Controller(object):
    def __init__(self, config):
        # setting up the control pins on relay switch
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

    def get_door_status(self, door_id):
        return
        {
            "id": d.id,
            "name": d.name,
            "last_state": d.last_state,
            "last_state_time": d.last_state_time
        }

    def get_all_statuses(self):
        statuses = [self.get_door_status(d.id) for d in self.doors]
        return statuses

        # door_allstat = [
        #     {
        #         "id": d.id,
        #         "name": d.name,
        #         "last_state": d.last_state,
        #         "last_state_time": d.last_state_time
        #     }
        #     for d in self.doors
        # ]

        # door_allstat = []
        # for d in self.doors:
        #     d = d.append(
        #         {
        #             "id": d.id,
        #             "name": d.name,
        #             "last_state": d.last_state,
        #             "last_state_time": d.last_state_time
        #         }
        #     )
        #  return door_allstat


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
