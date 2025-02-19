import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# init list with pin numbers
pinList = [12, 16, 20, 21]

# loop through pins and set mode and state to 'high'
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop
SleepTimeL = 2

# main loop
try:
  GPIO.output(12, GPIO.LOW)
  print ("ONE")
  time.sleep(SleepTimeL);
  GPIO.output(16, GPIO.LOW)
  print ("TWO")
  time.sleep(SleepTimeL);
  GPIO.output(20, GPIO.LOW)
  print ("THREE")
  time.sleep(SleepTimeL);
  GPIO.output(21, GPIO.LOW)
  print ("FOUR")
  time.sleep(SleepTimeL);
  GPIO.cleanup()
  print ("Good bye!")

# End program cleanly with keyboard
except KeyboardInterrupt:
  print ("  Quit")

  # Reset GPIO settings
  GPIO.cleanup()
