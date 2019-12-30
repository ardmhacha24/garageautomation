import RPi.GPIO as GPIO
import time
import sys
import signal

GPIO.setmode(GPIO.BCM)

# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground
# Bottom of door Sensor
DOOR_SENSOR_PIN_BOTTOM = 18
DOOR_SENSOR_PIN_TOP = 24

# Initially we don't know if the door sensor is open or closed...
isOpen = None
oldIsOpen = None

# Clean up when the user exits with keyboard interrupt
def cleanupLights(signal, frame):
    GPIO.cleanup()
    sys.exit(0)

# Set up the door sensor pin.
GPIO.setup(DOOR_SENSOR_PIN_BOTTOM, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(DOOR_SENSOR_PIN_TOP, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Set the cleanup handler for when user hits Ctrl-C to exit
signal.signal(signal.SIGINT, cleanupLights)

while True:
    print("oldIsOpen: ", oldIsOpen)
    oldIsOpen = isOpen
    print ("isOpen: ", isOpen)
    isOpen = GPIO.input(DOOR_SENSOR_PIN_BOTTOM)
    if (isOpen and (isOpen != oldIsOpen)):
        print ("Garge Door is Closed!")
    elif (isOpen != oldIsOpen):
        print ("Garage Door is Open!")
    time.sleep(0.1)