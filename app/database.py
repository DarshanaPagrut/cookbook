import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:password@db:27017/cookbook?authSource=admin")
    client = MongoClient(mongo_uri)
    return client["cookbook"]