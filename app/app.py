import os
import bcrypt
import jwt
import datetime

from flask import Flask, render_template, request, redirect, url_for
from database import get_db
from bson.objectid import ObjectId
from dotenv import load_dotenv
from functools import wraps

from redis_client import redis_client
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

db = get_db()

recipes_collection = db.recipes
users_collection = db.users


# JWT AUTH DECORATOR
def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.cookies.get("token")

        if not token:
            return redirect(url_for("login_page"))

        try:
            data = jwt.decode(
                token,
                app.secret_key,
                algorithms=["HS256"]
            )

            current_user = users_collection.find_one(
                {"_id": ObjectId(data["user_id"])}
            )

            if not current_user:
                return redirect(url_for("login_page"))

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login_page"))

        except jwt.InvalidTokenError:
            return redirect(url_for("login_page"))

        return f(current_user, *args, **kwargs)

    return decorated


# LANDING PAGE
@app.route('/')
def landing():
    return render_template("landing.html")


# REGISTER
@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            return "User already exists"

        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed
        })

        return redirect(url_for("login_page"))

    return render_template("register.html")


# LOGIN
@app.route('/login', methods=["GET", "POST"])
def login_page():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if not user:
            return "User not found"

        if bcrypt.checkpw(
            password.encode('utf-8'),
            user["password"]
        ):

            token = jwt.encode(
                {
                    "user_id": str(user["_id"]),
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                app.secret_key,
                algorithm="HS256"
            )

            response = redirect(url_for("index"))

            response.set_cookie(
                "token",
                token,
                httponly=True,
                samesite="Lax"
            )

            return response

        else:
            return "Invalid password"

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():

    response = redirect(url_for("landing"))
    response.delete_cookie("token")

    return response


# USER HOME
@app.route('/home')
@token_required
def index(current_user):

    user_id = str(current_user["_id"])
    cache_key = f"recipes:{user_id}"

    cached = redis_client.get(cache_key)

    if cached:
        print("CACHE HIT")
        recipes = json.loads(cached)

    else:
        print("CACHE MISS")

        recipes = list(recipes_collection.find({
            "user_id": user_id
        }))

        for r in recipes:
            r["_id"] = str(r["_id"])

        redis_client.setex(
            cache_key,
            60,
            json.dumps(recipes)
        )

    return render_template("index.html", recipes=recipes)

# VIEW RECIPE
@app.route('/recipe/<id>')
@token_required
def recipe(current_user, id):

    recipe = recipes_collection.find_one({
        "_id": ObjectId(id),
        "user_id": str(current_user["_id"])
    })

    return render_template("recipe.html", recipe=recipe)


# CREATE RECIPE
@app.route('/create-recipe', methods=['POST'])
@token_required
def create_recipe(current_user):

    recipe = {
        "title": request.form.get("title"),
        "image": request.form.get("image"),
        "description": request.form.get("description"),
        "ingredients": request.form.get("ingredients"),
        "instructions": request.form.get("instructions"),
        "tips": request.form.get("tips"),
        "servings": 2,
        "user_id": str(current_user["_id"])
    }

    recipes_collection.insert_one(recipe)

    return redirect(url_for("index"))


# DELETE RECIPE
@app.route('/delete/<id>', methods=["POST"])
@token_required
def delete_recipe(current_user, id):

    recipes_collection.delete_one({
        "_id": ObjectId(id),
        "user_id": str(current_user["_id"])
    })

    return redirect(url_for("index"))


# EDIT RECIPE
@app.route('/edit/<id>', methods=["GET", "POST"])
@token_required
def edit_recipe(current_user, id):

    recipe = recipes_collection.find_one({
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

        recipes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": updated}
        )

        return redirect(url_for("index"))

    return render_template("edit_recipe.html", recipe=recipe)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)