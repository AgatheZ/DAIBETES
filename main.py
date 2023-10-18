import os
from datetime import datetime
from databases.off import OpenFoodFacts

from flask import Flask, render_template, request, flash, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from secure import SecureHeaders
from utils.typesenseutils import createMongoClient, queryTypeSense, importToTypeSense
from typesense import Client
import pymongo

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
db_off = OpenFoodFacts()

# Define the database model for collected data
class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100))
    portion_size = db.Column(db.String(20))
    carb = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime)

    def __init__(self, food_name, portion_size, carb, timestamp):
        self.food_name = food_name
        self.carb = carb
        self.portion_size = portion_size
        self.timestamp = timestamp

#Initiate the clients 
mongo_client = pymongo.MongoClient("mongodb://root:toor@192.168.1.40:27017/")
client = Client({
    'nodes': [{'host': 'localhost', 'port': '8108', 'protocol': 'http'}],
    'api_key': 'test',
    'connection_timeout_seconds': 2
})


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
        res = db_off.get_product(food_name)
        entry = FoodEntry(food_name=res.name, portion_size=portion_size, carb = res.carb, timestamp=timestamp)
        db.session.add(entry)
        db.session.commit()

        flash('Data recorded successfully', 'success')

    current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('collect_data.html', current_timestamp=current_timestamp)

@app.route('/import_to_typesense', methods=['POST'])
def import_to_typesense():
    # Utilisez votre fonction importToTypeSense() ici
    importToTypeSense()  
    return "Importation terminée"

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    # Utilisez votre fonction queryTypeSense() ici
    results = queryTypeSense(query)
    return jsonify(results)

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
