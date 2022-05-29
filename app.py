from flask import (
    Flask,
    render_template,
    flash,
    request,
    url_for,
    request,
    session,
    redirect,
)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# import tensorflow as tf
# import cv2
# import numpy as np
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "SLR_user_login"
app.config["MYSQL_PORT"] = 3306
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in") == True:
        flash("You have already registerd & logged in", "info")
        return redirect("/section")
    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["password"]
        c_password = form["c_password"]
        if password != form["c_password"]:
            flash("Passwords do not match! Try again", "danger")
            return render_template("register.html")
        cur = mysql.connection.cursor()
        result = cur.execute("select email from user where email=%s", [email])
        if result == 1:
            flash("User already exists!!! ", "warning")
            return render_template("register.html")
        else:
            cur.execute(
                "insert into user(email, password) values(%s, %s)",
                (email, generate_password_hash(password)),
            )
            mysql.connection.commit()
            cur.close()
            flash("Registration successful! Please login", "success")
            return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in") == True:
        flash("You are already logged in", "info")
        return redirect("/section")
    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["password"]
        cur = mysql.connection.cursor()
        result = cur.execute("select * from user where email=%s", [email])
        if result > 0:
            data = cur.fetchone()
            db_password = data["password"]
            print(db_password)
            if check_password_hash(db_password, password):
                session["email"] = data["email"]
                session["logged_in"] = True
                flash(
                    "Welcome "
                    + session["email"]
                    + "! You have been logged in successfully ",
                    "success",
                )
                return redirect("/section")
            else:
                cur.close()
                flash("Password Does not match ", "danger")
                return render_template("login.html")
        else:
            cur.close()
            flash("User not found ", "danger")
            return render_template("login.html")
        cur.close()
        redirect("/section")
    return render_template("login.html")


@app.route("/section")
def section():
    if session.get("logged_in") == True:
        return render_template("section.html")
    else:
        flash("Please login first ", "warning")
        return redirect("/login")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/learn-digits")
def learnDigits():
    return render_template("learn-digits.html")


@app.route("/learn-alphabets")
def learnAlphabets():
    return render_template("learn-alphabets.html")


# Webcam code
@app.route("/webcam")
def webcam():
    if session.get("logged_in") == True:
        return render_template("cam.html")
    else:
        flash("Please login first ", "warning")
        return redirect("/login")


# Text to Image code
@app.route("/text", methods=["GET", "POST"])
def text_to_img():
    if session.get("logged_in") == True:
        if request.method == "POST":
            form = request.form
            text_ip = form["ip"]
            if text_ip.isalpha() or text_ip.isdigit():
                return render_template("text_img.html", img=text_ip)
            else:
                flash("Please enter appropriate alphabet or digit", "warning")
                return render_template("text_img.html")
        else:
            return render_template("text_img.html")
    else:
        flash("Please login first ", "warning")
        return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("email")
    session.pop("logged_in", None)
    flash("Logged Out successfully", "success")
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=5013)
