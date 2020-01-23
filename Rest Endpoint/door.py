import gpio
import time


class Door(object):
    last_action = None
    last_action_time = None

    def __init__(self, doorId, config):
        self.id = doorId
        self.name = config['name']
        self.open_pin = config['open_pin']
        self.close_pin = config['close_pin']
        self.closed_state_pin = config['closed_state_pin']
        self.opened_state_pin = config['opened_state_pin']
        self.pin_closed_value = config.get('pin_closed_value', 0)
        self.time_to_openclose = config.get('approx_time_to_openclose', 10)
        self.open_time = time.time()
        #initiatting open/close pins
        gpio.setup(self.open_pin, gpio.OUT)
        gpio.output(self.open_pin, True)
        gpio.setup(self.close_pin, gpio.OUT)
        gpio.output(self.close_pin, True)
        #initiating door status reed switches
        gpio.setup(self.closed_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.opened_state_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

    def get_state(self):
        if gpio.input(self.closed_state_pin) == self.pin_closed_value:
            return 'closed'
        elif self.last_action == 'open':
            if gpio.input(self.opened_state_pin) == self.pin_closed_value:
                return 'opened'
            elif (time.time() - self.last_action_time >= self.time_to_openclose) and (gpio.input(self.opened_state_pin) != self.pin_closed_value) and (gpio.input(self.closed_state_pin) != self.pin_closed_value):
                return 'opening error - taking too long'
            else:
                return 'opening'
        elif self.last_action ==  'close':
            if gpio.input(self.closed_state_pin) == self.pin_closed_value:
                return 'closed'
            elif (time.time() - self.last_action_time >= self.time_to_openclose) and (gpio.input(self.closed_state_pin) != self.pin_closed_value) and (gpio.input(self.opened_state_pin) != self.pin_closed_value):
                return 'closing error - taking too long'
            else:
                return 'closing'
        else:
            return 'opened'

    def toggle_relay(self, action):
        state = self.get_state()
        if (action == 'open') and (state == 'closed'):
            self.last_action = 'open'
            self.last_action_time = time.time()
            gpio.output(self.open_pin, False)
            time.sleep(0.2)
            gpio.output(self.open_pin, True)
        elif (action == 'close') and (state == 'opened'):
            self.last_action = 'close'
            self.last_action_time = time.time()
            gpio.output(self.close_pin, False)
            time.sleep(0.2)
            gpio.output(self.close_pin, True)
        elif (state == 'opening') or (state == 'closing'):
            print('Took no action - already moving... %s:%s:%s', (state, self.last_action,self.last_action_time))
        elif (state == 'opening error - taking too long') or (state == 'closing error - taking too long'):
            print('ERROR - investigate as taking too long... %s:%s:%s', (state, self.last_action,self.last_action_time))
        else:
            self.last_action = None
            self.last_action_time = None
