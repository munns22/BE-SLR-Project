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
    return render_template("section.html")


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
    flash("Its working fine", "info")
    return render_template("cam.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # fs = request.files['snap'] # it raise error when there is no `snap` in form
        fs = request.files.get("snap")
        if fs:
            print("FileStorage:", fs)
            print("filename:", fs.filename)
            fs.save("image.jpg")
            # img = cv2.imread('image.jpg')
            # print(img.shape) # Print image shape
            # cv2.imshow("original", img)

            # Cropping an image
            # cropped_image = img[32:256, 16:240]

            # Display cropped image
            # cv2.imshow("cropped", cropped_image)

            # Save the cropped image
            # cv2.imwrite("crop.jpg", cropped_image)
            classes = {
                0: "Zero",
                1: "One",
                2: "Two",
                3: "Three",
                4: "Four",
                5: "Five",
                6: "Six",
                7: "Seven",
                8: "Eight",
                9: "Nine",
            }

            # read model
            # model = tf.keras.models.load_model("vgg_gpu.h5")

            # read test img
            # test_img=cv2.imread('crop.jpg')

            # test_img=test_img.reshape(1,224,224,3)
            # rescale
            # test_img=test_img*(1./255)

            # predict
            # pred = model.predict(test_img)

            # ans=classes[np.argmax(pred)]
            # return "Your answer is:" +ans
            # flash("Your answer is: ",+ans, 'success')
        else:
            flash("You forgot snap! ", "danger")
    return "Hello World!"


# Text to Image code
@app.route("/text", methods=["GET", "POST"])
def text_to_img():
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


@app.route("/logout")
def logout():
    session.pop("email")
    session.pop("logged_in", None)
    flash("Logged Out successfully", "success")
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=5030)
