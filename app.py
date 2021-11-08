from flask import Flask, render_template
import pymongo

app = Flask(__name__)
try:
    mongo = pymongo.MongoClient(
        host = "localhost",
        port = 27017,
        serverSelectionTimeoutMS = 1000
    )

    # We Will Need to Create movies DB in Mongo Compass
    db = mongo.movies
    # Triggers Exception
    mongo.server_info()
except:
    print ("ERROR -- Cannot Connect to the DB.")

@app.route("/")
def homepage():
    return "<p> Hello, World! </p>"

if __name__ == "__main__":
    app.run(port = 8080, debug = True)