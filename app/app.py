"""
Main Flask application entry point using OOP architecture.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from functools import wraps
from bson.objectid import ObjectId

from database import Database
from redis_client import RedisClient
from auth_service import AuthService
from recipe_service import RecipeService


load_dotenv()


class RecipeApp:
    """
    Main application class that initializes Flask and services.
    """

    def __init__(self):
        """Initialize application services."""

        self.app = Flask(__name__)
        self.app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

        db = Database()
        redis_client = RedisClient()

        self.users = db.get_users_collection()
        self.recipes = db.get_recipes_collection()

        self.auth_service = AuthService(self.users, self.app.secret_key)
        self.recipe_service = RecipeService(self.recipes, redis_client)

        self.register_routes()

    def token_required(self, f):
        """JWT authentication decorator."""

        @wraps(f)
        def decorated(*args, **kwargs):

            token = request.cookies.get("token")

            if not token:
                return redirect(url_for("login_page"))

            user = self.auth_service.verify_token(token)

            if not user:
                return redirect(url_for("login_page"))

            return f(user, *args, **kwargs)

        return decorated

    def register_routes(self):
        """Register Flask routes."""

        app = self.app

        @app.route("/")
        def landing():
            return render_template("landing.html")

        @app.route("/register", methods=["GET", "POST"])
        def register():

            if request.method == "POST":

                user_id = self.auth_service.register_user(
                    request.form["username"],
                    request.form["email"],
                    request.form["password"]
                )

                if not user_id:
                    return "User already exists"

                return redirect(url_for("login_page"))

            return render_template("register.html")

        @app.route("/login", methods=["GET", "POST"])
        def login_page():

            if request.method == "POST":

                token = self.auth_service.login_user(
                    request.form["email"],
                    request.form["password"]
                )

                if not token:
                    return "Invalid credentials"

                response = redirect(url_for("index"))
                response.set_cookie("token", token, httponly=True, samesite="Lax")

                return response

            return render_template("login.html")

        @app.route("/home")
        @self.token_required
        def index(current_user):

            recipes = self.recipe_service.get_user_recipes(
                str(current_user["_id"])
            )

            return render_template("index.html", recipes=recipes)

        # CREATE RECIPE
        @app.route("/create-recipe", methods=["POST"])
        @self.token_required
        def create_recipe(current_user):

            recipe = {
                "title": request.form.get("title"),
                "image": request.form.get("image"),
                "description": request.form.get("description"),
                "ingredients": request.form.get("ingredients"),
                "instructions": request.form.get("instructions"),
                "tips": request.form.get("tips"),
                "servings": 2
            }

            self.recipe_service.create_recipe(
                recipe,
                str(current_user["_id"])
            )

            return redirect(url_for("index"))

        # DELETE RECIPE
        @app.route("/delete/<id>", methods=["POST"])
        @self.token_required
        def delete_recipe(current_user, id):

            self.recipe_service.delete_recipe(
                id,
                str(current_user["_id"])
            )

            return redirect(url_for("index"))

        # EDIT RECIPE
        @app.route("/edit/<id>", methods=["GET", "POST"])
        @self.token_required
        def edit_recipe(current_user, id):

            recipe = self.recipes.find_one({
                "_id": ObjectId(id),
                "user_id": str(current_user["_id"])
            })

            if not recipe:
                return redirect(url_for("index"))

            if request.method == "POST":

                updated = {
                    "title": request.form.get("title"),
                    "image": request.form.get("image"),
                    "description": request.form.get("description"),
                    "ingredients": request.form.get("ingredients"),
                    "instructions": request.form.get("instructions"),
                    "tips": request.form.get("tips")
                }

                self.recipe_service.update_recipe(
                    id,
                    updated,
                    str(current_user["_id"])
                )

                return redirect(url_for("index"))

            return render_template("edit_recipe.html", recipe=recipe)

        # VIEW RECIPE
        @app.route("/recipe/<id>")
        @self.token_required
        def recipe(current_user, id):

            recipe = self.recipes.find_one({
                "_id": ObjectId(id),
                "user_id": str(current_user["_id"])
            })

            return render_template("recipe.html", recipe=recipe)

    def run(self):
        """Run the Flask application."""
        self.app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    RecipeApp().run()

    