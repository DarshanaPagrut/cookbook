"""
Nginx routing test.
"""

import requests


def test_nginx_proxy():

    response = requests.get("http://localhost/")

    assert response.status_code == 200