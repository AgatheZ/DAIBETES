import os
from datetime import datetime

from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from secure import SecureHeaders

app = Flask(__name__)
app.secret_key = 'super secret key'
SESSION_TYPE = 'redis'
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/collect_data', methods=['GET', 'POST'])
def collect_data():
    if request.method == 'POST':
        food_name = request.form['food_name']
        portion_size = request.form['portion_size']
        timestamp = datetime.strptime(request.form['timestamp'], '%Y-%m-%dT%H:%M')
        
        entry = FoodEntry(food_name=food_name, portion_size=portion_size, timestamp=timestamp)
        db.session.add(entry)
        db.session.commit()

        flash('Data recorded successfully', 'success')

    current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('collect_data.html', current_timestamp=current_timestamp)

@app.route('/show_data')
def show_data():
    entries = FoodEntry.query.all()
    return render_template('show_data.html', entries=entries)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = FoodEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect('/show_data')

@app.after_request
def set_secure_headers(response):
    secure_headers.flask(response)
    return response

if __name__ == '__main__':
    with app.app_context():
        # Create the database tables
        db.create_all()
    
    app.secret_key = 'super secret key'
    app.debug = True
    app.run("0.0.0.0", port=8080, debug=True)
