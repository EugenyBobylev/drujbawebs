import json

import requests
from fastapi.encoders import jsonable_encoder

from backend import User
from backend import send_message
from config import BotConfig

auth = 'cXVlcnlfaWQ9QUFISFNXc0hBQUFBQU1kSmF3ZUxNU0FiJnVzZXI9JTdCJTIyaWQlMjIlM0ExMjQ0NzE3NTElMkMlMjJmaXJzdF9uYW1' \
       'lJTIyJTNBJTIyJUQwJTk1JUQwJUIyJUQwJUIzJUQwJUI1JUQwJUJEJUQwJUI4JUQwJUI5JTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIy' \
       'JUQwJTkxJUQwJUJFJUQwJUIxJUQxJThCJUQwJUJCJUQwJUI1JUQwJUIyJTIyJTJDJTIydXNlcm5hbWUlMjIlM0ElMjJCb2J5bGV2RUElM' \
       'jIlMkMlMjJsYW5ndWFnZV9jb2RlJTIyJTNBJTIyZW4lMjIlN0QmYXV0aF9kYXRlPTE2ODMxOTQzMzUmaGFzaD0yOTJhNzhiZmNhNjY1ZT' \
       'EwNGQ5ZDRmMDEzN2QwNWQxMjU0NzE3Yzc4MjAxYWMzYmJkMzcwMWQwYWU3MzFhZWQz'


# *************************************
# Required working backend
# *************************************
def check_get_root():
    url = 'http://127.0.0.1:8000/'
    headers = {
        'Authorization': auth
    }
    r = requests.get(url)
    assert r.status_code == 200


def check_create_user():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    user = User(id=123, name='test_user', timezone=1, birthdate='1966-12-15')
    user_json = jsonable_encoder(user)
    r = requests.post(url, headers=headers, json=user_json)
    assert r.status_code == 200


if __name__ == '__main__':
    check_create_user()