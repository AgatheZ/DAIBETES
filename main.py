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
from flask import request



# SETTINGS = get_config('config/deployment.cfg')

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import os
from secure import SecureHeaders

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.secret_key = 'super secret key'
app.config.from_object(__name__)
Bootstrap(app)
os.makedirs(os.path.join(os.getcwd(), 'logs'), exist_ok=True)
datetimetag = 'unknown'
secure_headers = SecureHeaders()

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define the database model for collected data
class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100))
    portion_size = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime)

    def __init__(self, food_name, portion_size, timestamp):
        self.food_name = food_name
        self.portion_size = portion_size
        self.timestamp = timestamp

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        food_name = request.form['food_name']
        portion_size = request.form['portion_size']
        timestamp = request.form['timestamp']

        entry = FoodEntry(food_name=food_name, portion_size=portion_size, timestamp=timestamp)
        db.session.add(entry)
        db.session.commit()

        return 'Data recorded successfully'

    return render_template('index.html')

@app.after_request
def set_secure_headers(response):
    secure_headers.flask(response)
    return response

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run("0.0.0.0", port=8080, debug=True)
