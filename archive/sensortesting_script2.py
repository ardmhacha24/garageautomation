import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)

# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground
# Bottom of door Sensor
DOOR_SENSOR_PIN_BOTTOM = 18
DOOR_SENSOR_PIN_TOP = 24

# Initially we don't know if the door sensor is open or closed...
BOTTOMisOpen = None
BOTTOMoldIsOpen = None
TOPisOpen = None
TOPoldIsOpen = None

# Set up the door sensor pin.
GPIO.setup(DOOR_SENSOR_PIN_BOTTOM, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DOOR_SENSOR_PIN_TOP, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# main loop
try:

    while True:
        BOTTOMoldIsOpen = BOTTOMisOpen
        TOPoldIsOpen = TOPisOpen

        BOTTOMisOpen = GPIO.input(DOOR_SENSOR_PIN_BOTTOM)
        TOPisOpen = GPIO.input(DOOR_SENSOR_PIN_TOP)

        if (BOTTOMisOpen and (BOTTOMisOpen != BOTTOMoldIsOpen)):
            print("Garage Door is Open!")
        elif (BOTTOMisOpen != BOTTOMoldIsOpen):
            print ("Garge Door is Closed!")
            time.sleep(0.1)

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quit")
    # Reset GPIO settings
    GPIO.cleanup()
    sys.exit(0)