# Stuff I need to add:
# 1. mag door sensors logic
# 2. Write to log actions of note for history
# 3. Endpoint to control via remotely
# 4. Rasp Controller health checking and alerting
# 4. SMTP Alerts

import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)

# init list with pin numbers
pinList = [12, 16, 20, 21]

user_input = None

# loop through pins and set mode and state to 'high' (aka OFF)
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop
SleepTimeL = 2

# main loop
try:

    while user_input != "Exit":
        user_input = input("Please enter a Open (o), Close (c), Stop (s) or Exit: ")
        if user_input == "Exit":
            GPIO.cleanup()
            print("Good bye!")
            break
        elif user_input == "Open" or user_input == "o":
            GPIO.output(12, GPIO.LOW)
            print("IN-ONE - Opening Doors")
            time.sleep(SleepTimeL)
            GPIO.output(12, GPIO.HIGH)
        elif user_input == "Close" or user_input == "c":
            GPIO.output(16, GPIO.LOW)
            print("IN-TWO - Closing Doors")
            time.sleep(SleepTimeL)
            GPIO.output(16, GPIO.HIGH)
        elif user_input == "Stop" or user_input == "s":
            GPIO.output(20, GPIO.LOW)
            print("IN-THREE - Stopping Doors Moving")
            time.sleep(SleepTimeL)
            GPIO.output(20, GPIO.HIGH)
        else:
            print("Input Error - Try again....")

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quit")
    # Reset GPIO settings
    GPIO.cleanup()
    sys.exit(0)