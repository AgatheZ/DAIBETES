import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from secure import SecureHeaders
from flask import Flask, render_template, session
from flask import send_file
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from config import get_config
from flask import request



SETTINGS = get_config('config/deployment.cfg')

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.secret_key = 'super secret key'
app.config.from_object(__name__)

Bootstrap(app)
os.makedirs(os.path.join(os.getcwd(), 'logs'), exist_ok=True)
datetimetag = 'unknown'
secure_headers = SecureHeaders()

@app.route('/', methods=["POST", "GET"])

def form():

    return render_template('index.html')

@app.after_request
def set_secure_headers(response):
    secure_headers.flask(response)
    return response



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True

    app.run("0.0.0.0", port=8080, debug=True)
