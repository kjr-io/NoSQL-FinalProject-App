import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask.globals import session
from flask.helpers import url_for
import pymongo
from bson.objectid import ObjectId
from pymongo.message import update

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
    db = mongo.nosql_movies
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
            session['plot'] = movie_found['fullplot']
            session['awards'] = movie_found['awards.wins']

            cast = movie_found['cast']
            castStripped = cast.strip("[]")
            session['cast'] = castStripped.replace('"', '')

            # This Appears Like a List but is Actually Just One String
            # Therefore to Output Correctly, the Data Must be Stripped & Replaced
            countries = movie_found['countries']
            countriesStripped = countries.strip("[]")
            session['countries'] = countriesStripped.replace('"', '')

            directors = movie_found['directors']
            directorsStripped = directors.strip("[]")
            session['directors'] = directorsStripped.replace('"', '')

            genres = movie_found['genres']
            genresStripped = genres.strip("[]")
            session['genres'] = genresStripped.replace('"', '')

            session['imdb.rating'] = movie_found['imdb.rating']
            session['imdb.votes'] = movie_found['imdb.votes']
            session['rated'] = movie_found['rated']
            session['year'] = movie_found['year']

            # To Return Comments
            session['_id'] = movie_found['_id']

            try:
                # Gathering Number of Comments to Iterate On if the User Comments
                session['num_comments'] = movie_found['num_mflix_comments']
            except:
                # If There are No Comments, Add the Column and Set to Zero
                db.movies.update_one({'_id': session['_id']}, {"$set": {"num_mflix_comments": "0"}})

            return redirect(url_for('movie_query'))

    # Greeting the Current User
    currentUser = session["name"]
    return render_template('logged_in.html', name=currentUser)

# Returning Movie Results
@app.route('/movie_query_results', methods=["POST", "GET", "PATCH"])
def movie_query():
    # Query to Find Comments Associated with the Movie the User Searched
    # Trying to Find Multiple Comments Here
    commentsList = []
    for doc in db.comments.find({"movie_id": session["_id"]}):
        commentsList.append(doc['text'] + ' by ' + doc['name'])

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

        # If the User Comments, We Have to Update Num Comments
        try:
            num_commentsInt = int(session['num_comments'])
            num_commentsInt += 1
            db.movies.update_one (
                {"_id": session["_id"]},
                {"$set": {"num_mflix_comments": str(num_commentsInt)}}
            )
            print(' * Counter Successfully Updated!')
        except:
            print(' * Counter Failed.')
        # If the User Comments, Redirect Them Back to the Page to Show the New Comment
        return redirect(url_for('movie_query'))
        
    # Rendering Page with Movie & Comment Information
    return render_template('movie_search.html', 
    title = session['title'],
    plot = session['plot'],
    awards = session['awards'],
    cast = session['cast'],
    countries = session['countries'],
    directors = session['directors'],
    genres = session['genres'],
    imdb_rating = session['imdb.rating'],
    imdb_votes = session['imdb.votes'], 
    rated = session['rated'],
    year = session['year'],
    text = commentsList
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
