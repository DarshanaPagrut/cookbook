"""
Recipe CRUD tests.
"""

import pytest


@pytest.fixture
def logged_in_client(client):
    """
    Create a logged-in user session.
    """

    client.post("/register", data={
        "username": "recipeuser",
        "email": "recipe@example.com",
        "password": "password123"
    })

    login = client.post("/login", data={
        "email": "recipe@example.com",
        "password": "password123"
    })

    token = login.headers.get("Set-Cookie")

    client.set_cookie("localhost", "token", token.split("token=")[1].split(";")[0])

    return client


def test_create_recipe(logged_in_client):
    """
    Test recipe creation.
    """

    response = logged_in_client.post("/create-recipe", data={
        "title": "Test Recipe",
        "image": "image.jpg",
        "description": "Test description",
        "ingredients": "salt",
        "instructions": "cook",
        "tips": "none"
    })

    assert response.status_code == 302


def test_view_home(logged_in_client):
    """
    Test viewing recipes page.
    """

    response = logged_in_client.get("/home")

    assert response.status_code == 200


def test_edit_recipe_route_exists(logged_in_client):
    """
    Ensure edit route exists.
    """

    response = logged_in_client.get("/edit/123456789012345678901234")

    assert response.status_code in (200, 302)


def test_delete_recipe_route_exists(logged_in_client):
    """
    Ensure delete route exists.
    """

    response = logged_in_client.post("/delete/123456789012345678901234")

    assert response.status_code in (302, 200)
    