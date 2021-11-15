import pandas as pd
from flask_pymongo import PyMongo

def csv_to_json(filename, header=None):
    data = pd.read_csv(filename, header = header)
    return data.to_dict('movies')

collection.insert_many(csv_to_json('your_file_path'))