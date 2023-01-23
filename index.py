from flask import Flask, render_template
import RPi.GPIO as GPIO
from pymongo import MongoClient
import urllib.request
import json
import textwrap
import os

cluster = MongoClient(os.environ.get("MONGO_URI"))
db = cluster["LibraryDB"]
collection = db["users"]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

app = Flask(__name__)
app.debug = True

# Home page route


@app.route("/")
def home():
    return render_template('home.html')

# Student pages route


@app.route("/student/home")
def irSensor():
    GPIO.setup(11, GPIO.IN)  # Read output from PIR motion sensor
    while True:
        i = GPIO.input(11)
        if i == 0:  # When output from motion sensor is HIGH
            return render_template('student-home.html', message=[
                "Student detected",
                "Place your barcode in front of the camera"
            ],
                mode="DETECTED")
        elif i == 1:
            return render_template('student-home.html', message=[
                "No Student detected"],
                mode="NOTDETECTED")
        else:
            return render_template('student-home.html', message=[
                "PIR sensor is not connected to the system"],
                mode="ERROR")


@app.route("/student/QRlogin")
def qrLogin():
    post = {"email": "yash123", "pid": "123", "password": "123"}
    collection.insert_one(post)
    return render_template('qrlogin.html')


@app.route("/student/store-book")
def booksApi():
    base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    with urllib.request.urlopen(base_api_link + "9781451648539") as f:
        text = f.read()
    decoded_text = text.decode("utf-8")
    # deserializes decoded_text to a Python object
    obj = json.loads(decoded_text)
    volume_info = obj["items"][0]
    authors = obj["items"][0]["volumeInfo"]["authors"]
    publisher = obj["items"][0]["volumeInfo"]["publisher"]
    image = obj["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]

    title = volume_info["volumeInfo"]["title"]
    description = textwrap.fill(
        volume_info["searchInfo"]["textSnippet"], width=65)
    pageCount = volume_info["volumeInfo"]["pageCount"]
    language = volume_info["volumeInfo"]["language"]

    return render_template('store-book.html', title=title, description=description, authors=authors, pageCount=pageCount, language=language, publisher=publisher, image=image)

# Admin pages route


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
