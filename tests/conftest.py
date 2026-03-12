"""
Pytest fixtures for Flask application testing.
"""

import pytest
from app import RecipeApp


@pytest.fixture
def app():
    """
    Create Flask test app.
    """
    recipe_app = RecipeApp()
    recipe_app.app.config["TESTING"] = True
    return recipe_app.app


@pytest.fixture
def client(app):
    """
    Flask test client.
    """
    return app.test_client()