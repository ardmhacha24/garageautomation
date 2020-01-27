import RPi.GPIO as gpio
import time
import sys

gpio.setmode(gpio.BCM)

# This is the gpio pin number we have the door sensors
opened_state_pin = 18
closed_state_pin = 24

pin_closed_value = 0
time_to_openclose = 7

# Set up the door sensor pin.
gpio.setup(opened_state_pin, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(closed_state_pin, gpio.IN, pull_up_down = gpio.PUD_UP)

last_action = None

# main loop
try:

    while last_action != "Exit":
        print("AAA=====")
        print('Sensor Closed: ', gpio.input(closed_state_pin))
        print('Sensor Open: ', gpio.input(opened_state_pin))
        print("AAA=====")

        last_action = input("Enter a open, close or check action... [Exit]: ")
        if last_action != 'check':
            copy_last_action = last_action
            last_action_time = time.time()

        time.sleep(3)
        print("AAA=====")
        print('copy_last_action: ', copy_last_action)
        print('last_action_time: ', last_action_time)
        print("AAA=====")

        if (gpio.input(closed_state_pin)) and \
                (not gpio.input(opened_state_pin)):
            print ('*** closed')
        elif (not gpio.input(closed_state_pin)) and \
                (gpio.input(opened_state_pin)):
            print ('*** opened')
        else:
            #if last_action == 'open':
            if copy_last_action == 'open':
                if (time.time() - last_action_time >= time_to_openclose) and (
                        gpio.input(opened_state_pin) != pin_closed_value) \
                        and (gpio.input(closed_state_pin) != pin_closed_value):
                    print ('*** ERROR: opening is taking too long...')
                else:
                    print ('*** opening')
            #elif last_action == 'close':
            elif copy_last_action == 'close':
                if (time.time() - last_action_time >= time_to_openclose) and (
                        gpio.input(closed_state_pin) != pin_closed_value) \
                        and (gpio.input(opened_state_pin) != pin_closed_value):
                    print ('*** ERROR: closing is taking too long...')
                else:
                    print ('*** closing')

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quitting Script")
    print("!!!=====")
    print('Sensor Closed: ', gpio.input(closed_state_pin))
    print('Sensor Open: ', gpio.input(opened_state_pin))
    print("!!!=====")
    # Reset gpio settings
    gpio.cleanup()
    sys.exit(0)