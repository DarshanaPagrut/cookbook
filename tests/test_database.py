"""
MongoDB integration tests.
"""


def test_recipe_insert_and_fetch(logged_in_client):

    create = logged_in_client.post("/create-recipe", data={
        "title": "DB Test Recipe",
        "image": "img.jpg",
        "description": "db test",
        "ingredients": "salt",
        "instructions": "cook",
        "tips": "none"
    })

    assert create.status_code == 302

    response = logged_in_client.get("/home")

    assert response.status_code == 200
    assert b"DB Test Recipe" in response.data