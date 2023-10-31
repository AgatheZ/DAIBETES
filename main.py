import os
from datetime import datetime
from databases.off import OpenFoodFacts
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from secure import SecureHeaders
from utils.typesenseutils import createMongoClient, queryTypeSense, importToTypeSense
from typesense import Client
import pymongo
import csv
from dateutil import parser

app = Flask(__name__)
app.secret_key = "super secret key"
SESSION_TYPE = "redis"
Bootstrap(app)
os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)
datetimetag = "unknown"
secure_headers = SecureHeaders()
# Configure SQLite database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
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


class FreeStyleData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    sugar_level = db.Column(db.Float)

    def __init__(self, timestamp, sugar_level):
        self.timestamp = timestamp
        self.sugar_level = sugar_level


# Initiate the clients
mongo_client = pymongo.MongoClient("mongodb://root:toor@192.168.1.40:27017/")
client = Client(
    {
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "api_key": "test",
        "connection_timeout_seconds": 2,
    }
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/model")
def model():
    return render_template("model.html")


@app.route("/collect_data", methods=["GET", "POST", "PUT"])
def collect_data():
    if request.method == "POST":
        food_name = request.form["food_name"]
        portion_size = request.form["portion_size"]
        timestamp = datetime.strptime(request.form["timestamp"], "%Y-%m-%dT%H:%M")

        typesense_results = queryTypeSense(food_name, query_field="name")

        if not typesense_results:
            flash("No product information found", "danger")
            return redirect(request.url)

        selected_product = typesense_results[0]

        entry = FoodEntry(
            food_name=selected_product["name"],
            portion_size=portion_size,
            carb=selected_product["carbohydrates"],
            timestamp=timestamp,
        )
        db.session.add(entry)
        db.session.commit()

        flash("Data recorded successfully", "success")
        return render_template(
            "collect_data.html",
            products=typesense_results,
            portion_size=portion_size,
            timestamp=timestamp,
        )
    # Handle GET request
    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template("collect_data.html", current_timestamp=current_timestamp)


@app.route("/upload_freestyle_data", methods=["GET", "POST"])
def upload_freestyle_data():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)
        if file:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                timestamp = parser.parse(row["time"])
                sugar_level = float(row["value"])
                entry = FreeStyleData(timestamp=timestamp, sugar_level=sugar_level)
                db.session.add(entry)
            db.session.commit()
            flash("Data uploaded successfully", "success")
    return render_template("collect_data.html")


@app.route("/show_data", methods=["GET", "POST"])
def show_data():
    food_entries = FoodEntry.query.all()
    freestyle_entries = FreeStyleData.query.all()
    return render_template(
        "show_data.html", food_entries=food_entries, freestyle_entries=freestyle_entries
    )


@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    entry = FoodEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect("/show_data")


@app.after_request
def set_secure_headers(response):
    secure_headers.flask(response)
    return response


@app.route("/query_typesense", methods=["GET"])
def query_typesense():
    query = request.args.get("query")
    typesense_results = queryTypeSense(query)
    return jsonify(typesense_results)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.secret_key = "super secret key"
    app.debug = True
    app.run("0.0.0.0", port=8011, debug=True)
