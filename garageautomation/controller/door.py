import RPi.GPIO as gpio
import time


class Door(object):
    def __init__(self, doorId, config):
        self.id = doorId
        self.name = config['name']
        self.open_pin = config['open_pin']
        self.close_pin = config['close_pin']
        self.closed_state_pin = config['closed_state_pin']
        self.opened_state_pin = config['opened_state_pin']
        self.pin_closed_value = config.get('pin_closed_value', 0)

        # setting up open/close pins
        gpio.setup(self.open_pin, gpio.OUT)
        gpio.output(self.open_pin, True)
        gpio.setup(self.close_pin, gpio.OUT)
        gpio.output(self.close_pin, True)
        # setting up door status reed switches
        gpio.setup(self.closed_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.opened_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

        # door action times and status
        self.time_to_openclose = config.get('approx_time_to_openclose', 10)
        self.open_time = time.time()
        self.last_action = None
        self.last_action_time = None
        self.last_state = self.get_state()
        self.last_state_time = time.time()

    def get_state(self):
        if (gpio.input(self.closed_state_pin) == self.pin_closed_value) and \
                (gpio.input(self.opened_state_pin) != self.pin_closed_value):
            return 'closed'
        elif gpio.input(self.opened_state_pin) == self.pin_closed_value and \
                (gpio.input(self.closed_state_pin) != self.pin_closed_value):
            return 'opened'
        else:
            if self.last_action == 'open':
                if (time.time() - self.last_action_time >= self.time_to_openclose) and (
                        gpio.input(self.opened_state_pin) != self.pin_closed_value) \
                        and (gpio.input(self.closed_state_pin) != self.pin_closed_value):
                    return 'ERROR: opening is taking too long...'
                else:
                    return 'opening'
            elif self.last_action == 'close':
                if (time.time() - self.last_action_time >= self.time_to_openclose) and (
                        gpio.input(self.closed_state_pin) != self.pin_closed_value) \
                        and (gpio.input(self.opened_state_pin) != self.pin_closed_value):
                    return 'ERROR: closing is taking too long...'
                else:
                    return 'closing'

    def toggle_relay(self, action_requested):
        door_current_state = self.get_state()
        print("A - action_requested:", action_requested, " [] current_door_state:", door_current_state)
        if (action_requested == 'open') and (door_current_state == 'closed'):
            self.last_action = 'open'
            self.last_action_time = time.time()
            gpio.output(self.open_pin, False)
            time.sleep(0.2)
            gpio.output(self.open_pin, True)
            print("B1 - action_requested:", action_requested, " [] current_door_state:", door_current_state)
            # pausing to allow movement from sensor
            time.sleep(6)
            print(time.time(), "B2 - action_requested:", action_requested, " [] current_door_state:", door_current_state)
            door_current_state = self.get_state()
            print(time.strftime('%X %x %Z'), "B3 - action_requested:", action_requested, " [] current_door_state:", door_current_state)
            # checking that the door is in movement
            if door_current_state == 'opening':
                print(time.strftime('%X %x %Z'), "B4 - action_requested:", action_requested, " [] current_door_state:",
                      door_current_state)
                return 'SUCCESS: Successful action - door opening'
            else:
                print(time.strftime('%X %x %Z'), "B5 - action_requested:", action_requested, " [] current_door_state:",
                      door_current_state)
                return ('ERROR: action failure - didnt kick off your requested action: %s:%s:%s', (
                    self.id, action_requested, self.last_action_time))
        elif (action_requested == 'close') and (door_current_state == 'opened'):
            self.last_action = 'close'
            self.last_action_time = time.time()
            gpio.output(self.close_pin, False)
            time.sleep(0.2)
            gpio.output(self.close_pin, True)
            # pausing to allow movement from sensor
            time.sleep(6)
            door_current_state = self.get_state()
            # checking that the door is in movement
            if door_current_state == 'closing':
                return 'SUCCESS: Successful action - door closing'
            else:
                return ('ERROR: action failure - didnt kick off your requested action: %s:%s:%s', (
                    self.id, action_requested, self.last_action_time))
        elif (door_current_state == 'opening') or (door_current_state == 'closing'):
            return ('INFO: Took no action - already moving... %s:%s:%s',
                    (door_current_state, self.last_action, self.last_action_time))
        elif (door_current_state == 'opening error - taking too long') or (
                door_current_state == 'closing error - taking too long'):
            return ('ERROR: action time to complete - investigate as taking too long... %s:%s:%s',
                    (door_current_state, action_requested, self.last_action_time))
        else:
            self.last_action = None
            self.last_action_time = None
            print("D1 - action_requested:", action_requested, " [] current_door_state:", door_current_state)
            return None
