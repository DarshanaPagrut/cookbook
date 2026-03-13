"""
Authentication service for handling user login, registration and JWT verification.
"""

import bcrypt
import jwt
import datetime
from bson.objectid import ObjectId


class AuthService:
    """
    Handles authentication logic.
    """

    def __init__(self, users_collection, secret_key):
        self.users_collection = users_collection
        self.secret_key = secret_key

    def register_user(self, username, email, password):
        """Register a new user."""

        existing_user = self.users_collection.find_one({"email": email})

        if existing_user:
            return None

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        user_id = self.users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed
        }).inserted_id

        return user_id

    def login_user(self, email, password):
        """Authenticate user and return JWT token."""

        user = self.users_collection.find_one({"email": email})

        if not user:
            return None

        if bcrypt.checkpw(password.encode(), user["password"]):

            token = jwt.encode(
                {
                    "user_id": str(user["_id"]),
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                self.secret_key,
                algorithm="HS256"
            )

            return token

        return None

    def verify_token(self, token):
        """Verify JWT token and return user."""

        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            user = self.users_collection.find_one({
                "_id": ObjectId(data["user_id"])
            })

            return user

        except Exception:
            return None

