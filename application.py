# I used a code from CS50 ProblemSet no.8. Thank you for that CS50 team !
import os
import sys
import psycopg2

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, error

# Configure application
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# To connect to a Postgresql heroku database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['postgres://jorqzsdckjpref:e757bbed8d7f33357c6c52e446df4b9863300b89ad7cdfbee42682a247e1e4cd@ec2-52-211-161-21.eu-west-1.compute.amazonaws.com:5432/d5gpufg0ht2tcv']
db = SQLAlchemy(app)

class workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

#global variable list for storing chosen picture
chosen_exercise = []

# default page
@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("history.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("username")
        if not name:
            return error("You must provide a name")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not password:
            return error("You must provide password")
        if not confirm:
            return error("You must confirm your password")
        if password != confirm:
            return error("Your passwords do not match, confirm identical password")
        else:
            db.execute("INSERT INTO user (username, hash) VALUES (?, ?)", name, generate_password_hash(password))

            rows = db.execute("SELECT * FROM user WHERE username = :username",
                          username=request.form.get("username"))

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return error("Invalid username or password !")

            session["user_id"] = rows[0]["id"]
            return redirect("/pickup")

    return redirect("/")


# Login function used from CS50 ProblemSet no.8. Thank you for that CS50 team !
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return error("You must provide username !")
        elif not request.form.get("password"):
            return error("You must provide password !")

        rows = db.execute("SELECT * FROM user WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return error("Invalid username or password !")

        session["user_id"] = rows[0]["id"]
        return redirect("/pickup")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# choose an exercise
@app.route("/pickup", methods=["GET", "POST"])
def pickup():
    if request.method == "GET":
        # read sql data into dict row
        rows = db.execute("SELECT exercise_name FROM exercise_list")
        return render_template("/pickup.html", rows=rows)
    else:
        # take chosen exercise, save into variable and then load query from db where chosen ex. name and picture name matches, so the picture can be rendered in html
        exlistname = request.form.get("exercise_list")
        # save chosen exercise into session, to be later used for database insertion line 144
        session["chosen_exercise"] = request.form.get("exercise_list")

        data = db.execute("SELECT picture_name FROM exercise_list WHERE exercise_name = ?", exlistname)
        session["picture_name"] = data[0]["picture_name"]
        return render_template("/exercise.html", chosen_exercise=session["picture_name"])

# Exercise function
# Choosing from various type of exercises show chosen exercise header and a picture,
# let user define amount of weight lifted, define number of repetitions and possible text comments
@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    if request.method == "GET":
        return render_template("exercise.html")
    else:
        # assign user input into variables, so these can be written into database
        # serie no.1
        series1 = request.form.get("series1")
        reps1 = request.form.get("reps1")
        weight1 = request.form.get("weight1")
        if not reps1:
            return error("You must provide reps amount !")
        if not weight1:
            return error("You must provide weight amount !")
        # serie no.2
        series2 = request.form.get("series2")
        reps2 = request.form.get("reps2")
        weight2 = request.form.get("weight2")
        if not reps2:
            return error("You must provide reps amount !")
        if not weight2:
            return error("You must provide weight amount !")
        # serie no.3
        series3 = request.form.get("series3")
        reps3 = request.form.get("reps3")
        weight3 = request.form.get("weight3")
        if not reps3:
            return error("You must provide reps amount !")
        if not weight3:
            return error("You must provide weight amount !")
        # serie no.4
        series4 = request.form.get("series4")
        reps4 = request.form.get("reps4")
        weight4 = request.form.get("weight4")
        if not reps4:
            return error("You must provide reps amount !")
        if not weight4:
            return error("You must provide weight amount !")

        #insert user input data into database
        db.execute("INSERT INTO history (id, exercise_name, series, reps, weight) VALUES (?, ?, ?, ?, ?),(?, ?, ?, ?, ?),(?, ?, ?, ?, ?),(?, ?, ?, ?, ?)",session["user_id"], session["chosen_exercise"], series1, reps1, weight1, session["user_id"], session["chosen_exercise"], series2, reps2, weight2, session["user_id"], session["chosen_exercise"], series3, reps3, weight3, session["user_id"], session["chosen_exercise"], series4, reps4, weight4)

        # apply whole logic
        return redirect("/pickup")


# show user's history, what exercise, amount of weights, number of repetitions was done by a user
@app.route("/history")
@login_required
def history():
    #select data to be shown based on user logged in
    rows = db.execute("SELECT datetime, exercise_name, series, reps, weight FROM history WHERE id = ?", session["user_id"])
    return render_template("history.html", rows=rows)
    
