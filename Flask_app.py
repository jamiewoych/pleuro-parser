from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import flask 
import flask-cors 
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Database configuration (Use SQLite for local testing, PostgreSQL for production)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salamander_inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Salamander(db.Model):
    animal_id = db.Column(db.String(10), primary_key=True)
    rack = db.Column(db.String(50))
    tank = db.Column(db.Integer)
    dob = db.Column(db.String(10))  # Store as a string (YYYY-MM-DD)
    species = db.Column(db.String(50))
    transgenic_status = db.Column(db.String(50))
    rfid = db.Column(db.String(20), nullable=True)
    protocol_number = db.Column(db.String(10))
    experimental_history = db.Column(db.JSON)

# Schema for serializing API responses
class SalamanderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Salamander

# Initialize Schema
salamander_schema = SalamanderSchema()
salamanders_schema = SalamanderSchema(many=True)

#Get all salamanders
@app.route('/api/salamanders', methods=['GET'])
def get_salamanders():
    all_salamanders = Salamander.query.all()
    return jsonify(salamanders_schema.dump(all_salamanders))

#Get single salamander
@app.route('/api/salamanders/<animal_id>', methods=['GET'])
def get_salamander(animal_id):
    salamander = Salamander.query.get_or_404(animal_id)
    return jsonify(salamander_schema.dump(salamander))

#Add new salamander
@app.route('/api/salamanders', methods=['POST'])
def add_salamander():
    data = request.get_json()
    new_salamander = Salamander(**data)
    db.session.add(new_salamander)
    db.session.commit()
    return jsonify(salamander_schema.dump(new_salamander)), 201

#Update inventory
@app.route('/api/salamanders/<animal_id>', methods=['PUT'])
def update_salamander(animal_id):
    salamander = Salamander.query.get_or_404(animal_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(salamander, key, value)
    db.session.commit()
    return jsonify(salamander_schema.dump(salamander))

#Update euthanasia log
@app.route('/api/salamanders/<animal_id>', methods=['DELETE'])
def delete_salamander(animal_id):
    salamander = Salamander.query.get_or_404(animal_id)
    db.session.delete(salamander)
    db.session.commit()
    return jsonify({"message": f"Salamander {animal_id} deleted."})

if __name__ == "__main__":
    app.run(debug=True)

