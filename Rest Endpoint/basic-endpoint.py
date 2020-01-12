# Testing flask as api endpoint

import time
import sys

from flask import Flask, render_template, request
#app = Flask(__name__, static_url_path='/static')

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route("/<door>/<action>", methods=['GET', 'POST'])
def action(door, action):
   return "Lets do somethimg with ths door.."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)