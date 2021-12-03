import os
import json
import pymongo
import pandas as pd

# Connecting to MongoDB
# ---------------------------------------------------------------- #
try:
    # Establishing Connection to localhost and Port the DB is Running On
    mongo = pymongo.MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 1000
    )
    # Selecting Our DB and Creating if Not Exist
    db = mongo.nosql_movies
    mongo.server_info()
    print(' * Success - Connection Established to the DB.')
except:
    print('ERROR - Could Not Connect to the DB.')

# Inserting Each File into the DB
# ---------------------------------------------------------------- #
# Setting Env Path to Data Directory
path = (str(os.getcwd()) + '/data')
os.chdir(path)

try: 

    # Creating All Collections
    db.create_collection("movies")
    db.create_collection("comments")
    db.create_collection("sessions")
    db.create_collection("theaters")
    db.create_collection("users")

    # Creating DF, Turning CSV to Dict, and Inserting into Colelction
    df = pd.read_csv('movies.csv')
    mongoDict = df.to_dict(orient = "records")
    db.movies.insert_many(mongoDict)

    df = pd.read_csv('comments.csv')
    mongoDict = df.to_dict(orient = "records")
    db.comments.insert_many(mongoDict)

    df = pd.read_csv('sessions.csv')
    mongoDict = df.to_dict(orient = "records")
    db.sessions.insert_many(mongoDict)

    df = pd.read_csv('theaters.csv')
    mongoDict = df.to_dict(orient = "records")
    db.theaters.insert_many(mongoDict)

    df = pd.read_csv('users.csv')
    mongoDict = df.to_dict(orient = "records")
    db.users.insert_many(mongoDict)

    print(' * Success - All Data Has Been Inserted into the DB.')
except:
    print(' * Failure - The Data Could Not Be Inserted to the DB.')


