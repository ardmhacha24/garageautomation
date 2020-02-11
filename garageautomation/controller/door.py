import logging
import time
import RPi.GPIO as gpio


class Door(object):
    def __init__(self, door_id, config):
        self.id = door_id
        self.name = config['name']
        self.open_pin = config['open_pin']
        self.close_pin = config['close_pin']
        self.closed_state_pin = config['closed_state_pin']
        self.opened_state_pin = config['opened_state_pin']
        # setting up logger
        self.logger = logging.getLogger(__name__)
        # setting up open/close pins
        gpio.setup(self.open_pin, gpio.OUT)
        gpio.output(self.open_pin, True)
        gpio.setup(self.close_pin, gpio.OUT)
        gpio.output(self.close_pin, True)
        # setting up door status reed switches
        gpio.setup(self.closed_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.opened_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        # door action times and status
        self.time_to_openclose = config['approx_time_to_openclose']
        # time to use in monitoring process to alert to user when opened for longer than set time
        self.opened_time = None
        self.last_action = None
        self.last_action_time = None
        self.last_state = self.get_state()
        self.last_state_time = time.time()

    def get_state(self):
        if (gpio.input(self.closed_state_pin)) and \
                (not gpio.input(self.opened_state_pin)):
            return 'closed'
        elif (not gpio.input(self.closed_state_pin)) and \
                (gpio.input(self.opened_state_pin)):
            return 'opened'
        else:
            if self.last_action == 'open':
                if (int(time.time() - self.last_action_time) >= self.time_to_openclose) and \
                        gpio.input(self.opened_state_pin) and \
                        gpio.input(self.closed_state_pin):
                    return 'ERROR: opening is taking too long...'
                else:
                    return 'opening'
            elif self.last_action == 'close':
                if (int(time.time() - self.last_action_time) >= self.time_to_openclose) and \
                        gpio.input(self.opened_state_pin) and \
                        gpio.input(self.closed_state_pin):
                    return 'ERROR: closing is taking too long...'
                else:
                    return 'closing'

    def toggle_relay(self, action_requested):
        door_current_state = self.get_state()
        if (action_requested == 'open') and (door_current_state == 'closed'):
            self.last_action = 'open'
            self.last_action_time = time.time()
            gpio.output(self.open_pin, False)
            time.sleep(0.2)
            gpio.output(self.open_pin, True)
            # pausing to allow movement from sensor
            time.sleep(2)
            door_current_state = self.get_state()
            # checking that the door is in movement
            if door_current_state == 'opening':
                return 'SUCCESS: Successful action - door opening'
            else:
                return ('ERROR: **OPEN** action failure - didnt kick off your requested action: %s:%s:%s', (
                    self.id, action_requested, self.last_action_time))
        elif (action_requested == 'close') and (door_current_state == 'opened'):
            self.last_action = 'close'
            self.last_action_time = time.time()
            gpio.output(self.close_pin, False)
            time.sleep(0.2)
            gpio.output(self.close_pin, True)
            # pausing to allow movement from sensor
            time.sleep(2)
            door_current_state = self.get_state()
            # checking that the door is in movement
            if door_current_state == 'closing':
                return 'SUCCESS: Successful action - door closing'
            else:
                return ('ERROR: **CLOSE** action failure - didnt kick off your requested action: %s:%s:%s', (
                    self.id, action_requested, self.last_action_time))
        elif (door_current_state == 'opening') or (door_current_state == 'closing'):
            return ('INFO: Took no action - already moving... %s:%s:%s',
                    (door_current_state, self.last_action, self.last_action_time))
        elif (door_current_state == 'opening error - taking too long') or (
                door_current_state == 'closing error - taking too long'):
            return ('ERROR: action time to complete - investigate as taking too long... %s:%s:%s',
                    (door_current_state, action_requested, self.last_action_time))
        else:
            # not doing anything as already in requested state - but will log that the ask occurred in further coding
            return None
