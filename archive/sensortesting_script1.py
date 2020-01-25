# Controller for single sensor on door

import RPi.GPIO as GPIO
import time
import sys
import signal

GPIO.setmode(GPIO.BCM)

# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground
DOOR_SENSOR_PIN = 18

# Initially we don't know if the door sensor is open or closed...
isOpen = None
oldIsOpen = None

# Clean up when the user exits with keyboard interrupt
def cleanupLights(signal, frame):
    GPIO.cleanup()
    sys.exit(0)

# Set up the door sensor pin.
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Set the cleanup handler for when user hits Ctrl-C to exit
signal.signal(signal.SIGINT, cleanupLights)

while True:
    oldIsOpen = isOpen
    isOpen = GPIO.input(DOOR_SENSOR_PIN)

    if (isOpen and (isOpen != oldIsOpen)):
        print("Garage Door is Open!")
        print ('A - values.... %s: %s', oldIsOpen, isOpen)
    elif (isOpen != oldIsOpen):
        print ("Garge Door is Closed!")
        print('B - values.... %s: %s', oldIsOpen, isOpen)
    time.sleep(0.1)