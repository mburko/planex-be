from flask import request


def test_run():
    res = request.post('http://localhost:5000/123',
                       json={
                           "login":"login",
                           "password": "password"}
                       )
    if res.ok:
        print(res.json())