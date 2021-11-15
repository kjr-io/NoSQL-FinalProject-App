import pandas as pd
from flask_pymongo import PyMongo

client = PyMongo.MongoClient("mongodb://localhost:27017")

def csv_to_json(filename, header=None):
    data = pd.read_csv(filename, header = header)
    return data.to_dict('movies')

movies.insert_many(csv_to_json('your_file_path'))

