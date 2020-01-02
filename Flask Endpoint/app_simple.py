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

door1Status = "close"
door2Status = "close"

doors = {
    1 : {'name' : 'Left Door', 'state' : door1Status},
    2 : {'name' : 'Right Door', 'state' : door2Status}
}

@app.route("/")
def main():
    for door in doors:
        doors[door]['state'] = "close"
        templateData = {
            'doors' : doors
        }
        return render_template('main.html', **templateData)

@app.route("/<action>", methods=['GET', 'POST'])
def action(action):
    global templateData
    deviceName = doors[1]['name']
    if action == "open":
        GPIO.output(12, GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(12, GPIO.HIGH)
        doors[1]['state'] = "open"
    if action == "close":
        GPIO.output(16, GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(16, GPIO.HIGH)
        doors[1]['state'] = "close"

	templateData = {
        'doors' : doors
    }
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
GPIO.cleanup()