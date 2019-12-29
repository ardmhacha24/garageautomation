import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# init list with pin numbers
pinList = [12, 16, 20, 21]

user_input = ""

# loop through pins and set mode and state to 'high'
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop
SleepTimeL = 2

# main loop
try:

    while user_input != "Exit":
        user_input = input("Please enter a Open, Close or Exit: ")
        if user_input == "Exit":
            GPIO.cleanup()
            print("Good bye!")
            break
        elif user_input == "Open":
            GPIO.output(12, GPIO.LOW)
            print("ONE - Opening")
            time.sleep(SleepTimeL)
        else:
            GPIO.output(16, GPIO.LOW)
            print("TWO - Closing")
            time.sleep(SleepTimeL)

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("  Quit")
    # Reset GPIO settings
    GPIO.cleanup()