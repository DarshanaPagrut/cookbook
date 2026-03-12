"""
JWT authentication tests.
"""

import jwt
import datetime


def test_expired_token(client, app):

    expired_token = jwt.encode(
        {
            "user_id": "123456789012345678901234",
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        },
        app.secret_key,
        algorithm="HS256"
    )

    client.set_cookie("localhost", "token", expired_token)

    response = client.get("/home")

    # Should redirect to login
    assert response.status_code == 302