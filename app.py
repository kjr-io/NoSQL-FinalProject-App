import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask.globals import session
from flask.helpers import url_for
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'testing'

# Connecting to MongoDB
# ---------------------------------------------------------------- #
try:
    # Establishing Connection to localhost and Port the DB is Running On
    mongo = pymongo.MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 1000
    )
    # Selecting Our DB
    db = mongo.nosql_movie_db
    mongo.server_info()
    print(' * Success - Database Running on localhost, port 27017')
except:
    print('ERROR - Could Not Connect to the DB.')

# CRUD Routes
# ---------------------------------------------------------------- #

# Log in
@app.route("/", methods=["POST", "GET"])
def login():
    message = 'Please Login to Your Account.'
    # If User is Already Signed in, Redirect to Logged In
    if "email" in session:
        return redirect(url_for("logged_in"))

    # If User Has Yet to Sign In
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Query Mongo for if the Email Exists
        email_found = db.users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            currentusername = email_found['name']
            
            # Checking to See if User Input Matches the Password Associated with the Email
            if password == passwordcheck:
                session["email"] = email_val
                session["name"] = currentusername
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                
                # Wrong Password, Sending "User Back to Login"
                message = 'Wrong Password.'
                return render_template('login.html', message=message)
        else:
            # Users Email Not Found in MongoDB
            message = 'Email Not Found.'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

# Logged In
@app.route('/logged_in', methods=["POST", "GET"])
def logged_in():
    if request.method == "POST":
        movie = request.form.get("movie")
        movie_found = db.movies.find_one({"title": movie})
        if movie_found:
            
            # Information to Give to User
            session['title'] = movie_found['title']
            session['awards'] = movie_found['awards']
            session['cast'] = movie_found['cast']
            session['countries'] = movie_found['countries']
            session['directors'] = movie_found['directors']
            session['genres'] = movie_found['genres']
            session['imdb'] = movie_found['imdb']
            session['rated'] = movie_found['rated']
            session['year'] = movie_found['year']

            # To Return Comments
            session['_id'] = movie_found['_id']

            return redirect(url_for('movie_query'))

    # Greeting the Current User
    currentUser = session["name"]
    return render_template('logged_in.html', name=currentUser)

# Returning Movie Results
@app.route('/movie_query_results', methods=["POST", "GET"])
def movie_query():
    # Query to Find Comments Associated with the Movie the User Searched
    movieComments = db.comments.find_one({"movie_id": session["_id"]})

    # Initializing These So There is No Error if No Comments
    session['text'] = "There are No Comments Yet!"
    session['commenter'] = None

    # If Movie Found Return Text with Commenter
    if movieComments:
        session['text'] = movieComments['text']
        session['commenter'] = movieComments['name']
    
    # User Comments if POST Request Received
    if request.method == "POST":
        comment = {
            "date":datetime.datetime.utcnow(),
            "email":session["email"],
            "movie_id":session["_id"],
            "name":session["name"],
            "text":request.form["usercomment"]
        }
        dbResponse = db.comments.insert_one(comment)
        print(dbResponse.inserted_id)

    # Rendering Page with Movie & Comment Information
    return render_template('movie_search.html', 
    title = session['title'],
    awards = session['awards'],
    cast = session['cast'],
    countries = session['countries'],
    directors = session['directors'],
    genres = session['genres'],
    imdb = session['imdb'], 
    rated = session['rated'],
    year = session['year'],
    text = session['text'],
    commenter = session['commenter']
    ) 

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
            "name":request.form["name"],
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
