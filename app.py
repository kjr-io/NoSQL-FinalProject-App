from flask import Flask, render_template, request, url_for, redirect, session
from flask.globals import session
from flask.helpers import url_for
#from flask.wrappers import Response
#from flask_pymongo import PyMongo
import pymongo
import bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'testing'

# Connecting to MongoDB
# ---------------------------------------------------------------- #
try:
    mongo = pymongo.MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 1000
    )
    db = mongo.nosql_movie_db
    mongo.server_info()
    print(' * Success - Database Running on localhost, port 27017')
except:
    print('ERROR - Could Not Connect to the DB.')


# Constructing the Routes
# ---------------------------------------------------------------- #
# Home Page Route "localhost/"
'''
@app.route("/")
def homepage():
    return render_template('login.html')
'''

# CRUD Routes
# ---------------------------------------------------------------- #

# Create an Account
'''
@app.route("/", methods=['POST', 'GET'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = db.users.find_one({"name": user})
        email_found = db.users.find_one({"email": email})
        if user_found:
            message = 'There Already is a User by that Name.'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This Email Already Exists in Database.'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords Should Match.'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            db.users.insert_one(user_input)
            
            user_data = db.users.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')
'''

# Log in
@app.route("/", methods=["POST", "GET"])
def login():
    message = 'Please Login to Your Account.'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = db.users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            #if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            if password == passwordcheck:
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong Password.'
                return render_template('login.html', message=message)
        else:
            message = 'Email Not Found.'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

# Logged In
@app.route('/logged_in')
def logged_in():
    if "email" in session:
        print(session)
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

# Log Out
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('login.html')




# CRUD Operation Examples
# ---------------------------------------------------------------- #

# Create Document Routes
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = {
            "email":request.form["email"],
            "name" :request.form["name"],
            "password":request.form["password"]
        }
        dbResponse = db.users.insert_one(user)
        print(dbResponse.inserted_id)
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
    except Exception as ex:
        print(ex)

# Update Document Routes
@app.route("/users/<id>", methods=["PATCH"])
def update_user(id):
    try:
        dbResponse = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": request.form["name"]}}
        )
        if dbResponse.modified_count == 1:
            print('Updated.')
        else:
            print('Nothing to Update')
    except Exception as ex:
        print('Sorry Cannot Update')


# Delete Document Routes
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({"_id": ObjectId(id)})
        if dbResponse.deleted_count == 1:
            print('User Deleted')
        else: 
            print('User not Found')
    except Exception as ex:
        print('Cannot Delete User')


# Starting the Web Server
# ---------------------------------------------------------------- #
if __name__ == "__main__":
    # Running on Port 8080
    app.run(port = 8080, debug = True)
