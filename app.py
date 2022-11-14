from flask import Flask, redirect, url_for, render_template, request
from models import db
from secret import *

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

# db.create_all()


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def Login():
    return render_template("login.html")





if __name__ == "__main__":
    app.run(port=3000)
