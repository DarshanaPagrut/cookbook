import os
from flask import Flask, render_template, request, redirect, url_for
from database import get_db
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

db = get_db()
recipes_collection = db.recipes


@app.route('/')
def index():
    recipes = list(recipes_collection.find())
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/<id>')
def recipe(id):

    recipe = recipes_collection.find_one({"_id": ObjectId(id)})
    return render_template("recipe.html", recipe=recipe)


@app.route('/create-recipe', methods=['POST'])
def create_recipe():

    recipe = {
        "title": request.form.get("title"),
        "image": request.form.get("image"),
        "description": request.form.get("description"),
        "ingredients": request.form.get("ingredients"),
        "instructions": request.form.get("instructions"),
        "tips": request.form.get("tips"),
        "servings": 2
    }

    recipes_collection.insert_one(recipe)

    return redirect(url_for("index"))


@app.route('/delete/<id>', methods=["POST"])
def delete_recipe(id):

    recipes_collection.delete_one({"_id": ObjectId(id)})

    return redirect(url_for("index"))


@app.route('/edit/<id>', methods=["GET","POST"])
def edit_recipe(id):

    recipe = recipes_collection.find_one({"_id": ObjectId(id)})

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