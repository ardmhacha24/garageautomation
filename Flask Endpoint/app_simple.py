# Testing flask as api endpoint

import RPi.GPIO as GPIO
import time
import sys

from flask import Flask, render_template, request
app = Flask(__name__, static_url_path='/static')

# time to sleep between operations in the main loop
SleepTimeL = 2

GPIO.setmode(GPIO.BCM)
# init list with pin numbers
pinList = [12, 16, 20, 21]

# loop through pins and set mode and state to 'high' (aka OFF)
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop
SleepTimeL = 2

doors = {
    1 : {'name' : 'Left Door', 'state' : "close"},
    2 : {'name' : 'Right Door', 'state' : "close"}
}
doors_GPIOpins = {
    1 : {'open' : 12, 'closed' : 16},
    2 : {'open' : 20, 'closed' : 21}
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
    if action == "open":
        GPIO.output(doors_GPIOpins[door]['open'], GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(doors_GPIOpins[door]['open'], GPIO.HIGH)
        doors[door]['state'] = "open"
    if action == "close":
        GPIO.output(doors_GPIOpins[door]['close'], GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(doors_GPIOpins[door]['close'], GPIO.HIGH)
        doors[1]['state'] = "close"

    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
GPIO.cleanup()