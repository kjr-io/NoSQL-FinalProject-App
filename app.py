import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask.globals import session
from flask.helpers import url_for
import pymongo
from bson.objectid import ObjectId
from pymongo.message import update
import math

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

        # Looking for Requested Movie from Form, Passing to Mongo
        movie = request.form.get("movie")
        movie_found = db.movies.find_one({"title": movie})
        if movie_found:
            
            # Information to Give to User
            session['title'] = movie_found['title']
            session['poster'] = movie_found['poster']
            session['plot'] = movie_found['fullplot']
            session['awards'] = movie_found['awards_wins']

            # This Appears Like a List but is Actually Just One String
            # Therefore to Output Correctly, the Data Must be Stripped & Replaced
            cast = movie_found['cast']
            castStripped = cast.strip("[]")
            session['cast'] = castStripped.replace('"', '')

            countries = movie_found['countries']
            countriesStripped = countries.strip("[]")
            session['countries'] = countriesStripped.replace('"', '')

            directors = movie_found['directors']
            directorsStripped = directors.strip("[]")
            session['directors'] = directorsStripped.replace('"', '')

            genres = movie_found['genres']
            genresStripped = genres.strip("[]")
            session['genres'] = genresStripped.replace('"', '')

            # Gathering Other Information Useful to the User 
            session['imdb_rating'] = movie_found['imdb_rating']
            session['imdb_votes'] = movie_found['imdb_votes']
            session['rated'] = movie_found['rated']
            session['year'] = movie_found['year']

            # To Return Comments
            session['_id'] = movie_found['_id']

            try:
                # Gathering Number of Comments to Iterate On if the User Comments
                session['num_comments'] = movie_found['num_mflix_comments']

                # If num_mflix_comments is NaN, Set it to Zero
                if int(session['num_comments']) < 0:
                    db.movies.update_one({'_id': session['_id']}, {"$set": {"num_mflix_comments": "0"}})
                
            except:
                # If There are No Comments Field, Add the Field and Set to Zero
                db.movies.update_one({'_id': session['_id']}, {"$set": {"num_mflix_comments": "0"}})

            return redirect(url_for('movie_query'))

    # Greeting the Current User
    currentUser = session["name"]
    return render_template('logged_in.html', name=currentUser)

# Returning Movie Results
# Stored Outside of a Route so Delete Can Access the List
commentIdList = []
@app.route('/movie_query_results', methods=["POST", "GET"])
def movie_query():
    # Query to Find Comments Associated with the Movie the User Searched
    # Trying to Find Multiple Comments Here
    commentsList = []

    # Clearing the List Whenever Page is Refreshed, Prevents Duplicates Since List is Outside the Route
    commentIdList.clear()

    # Finding All of the Comments and Appending to a List
    # commentsList is to be Rendered on the Page, Best Way to Pass Many to Jinja
    # commentIdList is so We Can Identify Which Comment to Delete by the _id
    for doc in db.comments.find({"movie_id": session["_id"]}):
        commentsList.append(doc['text'] + ' by ' + doc['name'])
        commentIdList.append(doc['_id'])
    print(commentIdList)

    # User Comments if POST Request Received
    if request.method == "POST":
        if 'usercomment' in request.form:
            # Gather All Information for New Comment Document and Insert it
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
                # Grabs as Int, Iterates by One, Stores it Back as a String (Data Type in the DB)
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
        if 'userrating' in request.form:
            try:
                currentRating = session['imdb_rating']
                updatedVotes = session['imdb_votes']

                # Gathering the User Rating and Recalculating the Average
                userRatingForm = int(request.form["userrating"])
                updatedRatings = round((((currentRating * updatedVotes) + userRatingForm)/(updatedVotes + 1)), 2)

                # Iterating Votes
                updatedVotes += 1

                # Update Votes and Rating using update_many
                db.movies.update_many (
                    {"_id": session["_id"]},
                    {"$set": {"imdb_votes": updatedVotes, "imdb_rating": updatedRatings}}
                )
                print(' * Counter Successfully Updated!')
                print(' * Rating Successfully Updated!')
                return redirect(url_for('movie_query'))
            except:
                print(' * Counter & Rating Failed.')
            return redirect(url_for('movie_query'))

    # Rendering Page with Movie & Comment Information
    return render_template('movie_search.html', 
    title = session['title'],
    poster = session['poster'],
    plot = session['plot'],
    awards = session['awards'],
    cast = session['cast'],
    countries = session['countries'],
    directors = session['directors'],
    genres = session['genres'],
    imdb_rating = session['imdb_rating'],
    imdb_votes = session['imdb_votes'], 
    rated = session['rated'],
    year = session['year'],
    text = commentsList
    )

# Deleting Comment
@app.route('/delete/<index>', methods=["GET", "POST"])
def delete(index):
    try:
        # Creating var Based off of Jinja Index (loop.index0) Which Helps us Determine Which Comment is What
        var = int(index)
        # Retrieving this Comment's _id in the commentIdList
        objId = str(commentIdList[var])
        try:
            # If User Made Comment
            dbResponse = db.comments.delete_one({"_id": ObjectId(objId)})
        except:
            # If Comment Previously Existed in the DB
            dbResponse = db.comments.delete_one({"_id": objId})
        if dbResponse.deleted_count == 1:
            print(' * Comment Deleted.')
        else: 
            print('* Comment not Found.')
        return redirect(url_for('movie_query'))
    except:
        print('Cannot Delete Comment.')
        return redirect(url_for('movie_query'))

# Log Out
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('login.html')

# Starting the Web Server
# ---------------------------------------------------------------- #
if __name__ == "__main__":
    # Running on Port 8080
    app.run(port = 8080, debug = True)
