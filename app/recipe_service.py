"""
Recipe service containing business logic for recipe CRUD operations.
"""

import json
from bson.objectid import ObjectId


class RecipeService:
    """
    Handles recipe operations and caching.
    """

    def __init__(self, recipes_collection, redis_client):
        self.recipes_collection = recipes_collection
        self.redis = redis_client

    def get_user_recipes(self, user_id):
        """Fetch recipes with Redis caching."""

        cache_key = f"recipes:{user_id}"

        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        recipes = list(self.recipes_collection.find({"user_id": user_id}))

        for r in recipes:
            r["_id"] = str(r["_id"])

        self.redis.set(cache_key, json.dumps(recipes), expire=60)

        return recipes

    def create_recipe(self, recipe, user_id):
        """Create recipe and invalidate cache."""

        recipe["user_id"] = user_id

        self.recipes_collection.insert_one(recipe)

        self.redis.delete(f"recipes:{user_id}")

    def delete_recipe(self, recipe_id, user_id):
        """Delete recipe and invalidate cache."""

        self.recipes_collection.delete_one({
            "_id": ObjectId(recipe_id),
            "user_id": user_id
        })

        self.redis.delete(f"recipes:{user_id}")

    def update_recipe(self, recipe_id, updated, user_id):
        """Update recipe and invalidate cache."""

        self.recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": updated}
        )

        self.redis.delete(f"recipes:{user_id}")

        