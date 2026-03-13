"""
MongoDB database connection module.
Provides a singleton-style database manager with connection pooling.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class Database:
    """
    Handles MongoDB connection and provides access to collections.
    """

    def __init__(self):
        """
        Initialize MongoDB connection using environment variables.
        """
        mongo_uri = os.getenv(
            "MONGO_URI",
            "mongodb://root:password@db:27017/cookbook?authSource=admin"
        )

        self.client = MongoClient(
            mongo_uri,
            maxPoolSize=50,
            minPoolSize=5
        )

        self.db = self.client["cookbook"]

    def get_users_collection(self):
        """Return users collection."""
        return self.db.users

    def get_recipes_collection(self):
        """Return recipes collection."""
        return self.db.recipes

        