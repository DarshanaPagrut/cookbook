"""
Authentication related tests.
"""

def test_register_user(client):
    """
    Test user registration.
    """

    response = client.post("/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code in (302, 200)


def test_login_user(client):
    """
    Test login functionality.
    """

    client.post("/register", data={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    })

    response = client.post("/login", data={
        "email": "test2@example.com",
        "password": "password123"
    })

    assert response.status_code == 302
    