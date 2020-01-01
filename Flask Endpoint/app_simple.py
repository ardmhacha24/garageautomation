# Testing flask as api endpoint

import RPi.GPIO as GPIO
import time
import sys

from flask import Flask, render_template, request
app = Flask(__name__, static_url_path='/static')

# time to sleep between operations in the main loop
SleepTimeL = 2

GPIO.setmode(GPIO.BCM)
pins = {
    12 : {'name' : 'Garage Door Open', 'state' : GPIO.HIGH},
    16 : {'name' : 'Garage Door Close', 'state' : GPIO.HIGH},
    20 : {'name' : 'Garage Door Stop', 'state' : GPIO.HIGH}
}

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

@app.route("/")
def main():
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
        templateData = {
            'pins' : pins
        }
        return render_template('main.html', **templateData)

@app.route("/<changePin>/<action>", methods=['GET', 'POST'])
def action(changePin, action):
    changePin = int(changePin)
    deviceName = pins[changePin]['name']
    if action == "open":
        GPIO.output(changePin, GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(changePin, GPIO.HIGH)
    if action == "close":
        GPIO.output(changePin, GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(changePin, GPIO.HIGH)
    if action == "stop":
        GPIO.output(changePin, GPIO.LOW)
        time.sleep(SleepTimeL)
        GPIO.output(changePin, GPIO.HIGH)


	#for pin in pins:
     #       pins[pin]['state'] = GPIO.input(pin)
    #templateData = {
     #   'pins' : pins
    #}
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
GPIO.cleanup()