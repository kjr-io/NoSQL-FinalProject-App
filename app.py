from flask import Flask, render_template, Response, Request
from flask.wrappers import Response
from flask_pymongo import PyMongo
import pymongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

# Connecting to MongoDB
# ---------------------------------------------------------------- #
try:
    mongo = pymongo.MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 1000
    )
    db = mongo.nosql-final-project
    mongo.server_info()
except:
    print('ERROR - Could Not Connect to the DB.')

'''
app.config["MONGO_URI"] = "mongodb://localhost:27017/nosql-finalproject"
mongo = PyMongo(app)
'''

# Constructing the Routes
# ---------------------------------------------------------------- #
# Home Page Route "localhost/"
@app.route("/")
def homepage():
    return render_template('index.html')

# CRUD Operation Routes
# ---------------------------------------------------------------- #

# Create Document Routes
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = {
            "email":Request.form["email"],
            "name" :Request.form["name"],
            "password":Request.form["password"]
        }
        dbResponse = db.users.insert_one(user)
        print(dbResponse.inserted_id)
        return Response(
            response = json.dumps({"Message": "User Create", "id": f"{dbResponse.inserted_id}"}),
            status = 200,
            mimetype = "Application/JSON"
        )
    except Exception as ex:
        print(ex)

# Read Document Routes
@app.route("/users", methods=["GET"])
def get_some_user():
    try:
        data = list(db.users.find())
        print(data)
        for user in data:
            user["_id"] = str(user["_id"])
        return Response(
            response = json.dumps(data),
            status = 200,
            mimetype = "Application/JSON"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response = json.dumps({"Message": "Cannot Create User."}),
            status = 500,
            mimetype = "Application/JSON"
        )

# Update Document Routes
@app.route("/users/<id>", methods=["PATCH"])
def update_user(id):
    try:
        dbResponse = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": Request.form["name"]}}
        )
        if dbResponse.modified_count == 1:
            return Response(
                response = json.dumps({"Message": "User Updated"}),
                status = 200,
                mimetype = "Application/JSON"
            )
        else:
            return Response(
                response = json.dumps({"Message": "Nothing to Update "}),
                status = 200,
                mimetype = "Application/JSON"
            )
    except Exception as ex:
        response = json.dumps(
            response = json.dumps({"message": "Sorry Cannot Update User."}),
            status = 500,
            mimetype = "Application/JSON"
        )

# Delete Document Routes
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({"_id": ObjectId(id)})
        if dbResponse.deleted_count == 1:
            response = json.dumps(
                response = json.dumps({"message": "User Deleted", "id":f"{id}"}),
                status = 200,
                mimetype = "Application/JSON"
            )
        else: 
            response = json.dumps(
                response = json.dumps({"message": "User Not Found", "id":f"{id}"}),
                status = 200,
                mimetype = "Application/JSON"
            )
    except Exception as ex:
        response = json.dumps(
            response = json.dumps({"message": "Sorry Cannot Delete User."}),
            status = 500,
            mimetype = "Application/JSON"
        )


# Starting the Web Server
# ---------------------------------------------------------------- #
if __name__ == "__main__":
    # Running on Port 8080
    app.run(port = 8080, debug = True)
