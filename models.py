from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __table_name__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    

class ToDO(db.Model):
    __table_name__ = 'todo'
    to_do = db.Column(db.Integer, primary_key=True)
    
