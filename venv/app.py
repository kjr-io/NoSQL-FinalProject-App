from flask import Flask, render_template
from flask_pymongo import PyMongo
import json

app = Flask(__name__)

# Connecting to MongoDB
# ---------------------------------------------------------------- #
app.config["MONGO_URI"] = "mongodb://localhost:27017/nosql-finalproject"
mongo = PyMongo(app)

# Constructing the Routes
# ---------------------------------------------------------------- #
# Home Page Route "localhost/"
@app.route("/")
def homepage():
    return render_template('login.html')


@app.route("/")
def index():
    return render_template('index.html', name=first_name)

# Starting the Web Server
# ---------------------------------------------------------------- #
if __name__ == "__main__":
    # Running on Port 8080
    app.run(port = 8080, debug = True)
