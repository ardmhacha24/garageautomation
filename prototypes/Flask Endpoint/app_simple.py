# Testing flask as api endpoint

import RPi.GPIO as GPIO
import time
import sys

from flask import Flask, render_template, request
app = Flask(__name__, static_url_path='/static')

GPIO.setmode(GPIO.BCM)
# init list with pin numbers
pinList = [12, 16, 20, 21]

# loop through pins and set mode and state to 'high' (aka OFF)
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop
SleepTimeL = 0.2

doors = {
    "Left" : {'name' : 'Left Door', 'state' : "close"},
    "Right" : {'name' : 'Right Door', 'state' : "close"}
}
doors_GPIOpins = {
    "Left" : {'open' : 12, 'close' : 16},
    "Right" : {'open' : 20, 'close' : 21}
}

global templateData
templateData = {
    'doors' : doors
}

@app.route("/")
def main():
    return render_template('main.html', **templateData)

@app.route("/<door>/<action>", methods=['GET', 'POST'])
def action(door, action):
   # need to do som sanity checking and error handling...
   GPIO.output(doors_GPIOpins[door][action], GPIO.LOW)
   time.sleep(SleepTimeL)
   GPIO.output(doors_GPIOpins[door][action], GPIO.HIGH)
   doors[door]['state'] = action

   return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
GPIO.cleanup()