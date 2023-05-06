import json

import requests

from backend.backend import User
from config import BotConfig

auth = 'cXVlcnlfaWQ9QUFISFNXc0hBQUFBQU1kSmF3ZUxNU0FiJnVzZXI9JTdCJTIyaWQlMjIlM0ExMjQ0NzE3NTElMkMlMjJmaXJzdF9uYW1' \
       'lJTIyJTNBJTIyJUQwJTk1JUQwJUIyJUQwJUIzJUQwJUI1JUQwJUJEJUQwJUI4JUQwJUI5JTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIy' \
       'JUQwJTkxJUQwJUJFJUQwJUIxJUQxJThCJUQwJUJCJUQwJUI1JUQwJUIyJTIyJTJDJTIydXNlcm5hbWUlMjIlM0ElMjJCb2J5bGV2RUElM' \
       'jIlMkMlMjJsYW5ndWFnZV9jb2RlJTIyJTNBJTIyZW4lMjIlN0QmYXV0aF9kYXRlPTE2ODMxOTQzMzUmaGFzaD0yOTJhNzhiZmNhNjY1ZT' \
       'EwNGQ5ZDRmMDEzN2QwNWQxMjU0NzE3Yzc4MjAxYWMzYmJkMzcwMWQwYWU3MzFhZWQz'


# *************************************
# Required working backend
# *************************************
def test_create_user_without_auth():
    url = 'http://127.0.0.1:8000/user/'
    user = User(name='test_user', timezone=1)
    r = requests.post(url, json=user.__dict__)
    assert r.status_code == 422


def test_create_user_with_auth():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Authorization': auth
    }
    user = User(name='test_user', timezone=1)
    r = requests.post(url, headers=headers, json=user.__dict__)
    assert r.status_code == 200


def test_create_user_with_wrong_auth():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Authorization': 'all nonsense'
    }
    user = User(name='test_user', timezone=1)
    r = requests.post(url, headers=headers, json=user.__dict__)
    assert r.status_code == 401


def test_api_bot_send_me():
    headers = {
        'Content-Type: application/json'
    }
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/getMe'
    r = requests.get(url)
    assert 200 == r.status_code
    answer = r.json()
    assert answer['ok']
    assert 'conceptui' == answer['result']['first_name']
    assert 'conceptuibot' == answer['result']['username']


def test_answer_web_app_query():
    '''
    Тест на отправку боту данных из WebApp
    перед выполнение,каждый раз, требуется обновлять web_query_id
    т.к. он может быть использован только единожды
    :return:
    '''
    web_query_id = 'AAHHSWsHAAAAAMdJawcBvcwJ'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'web_app_query_id': web_query_id,
        'result': {
            'type': 'article',
            'id': '123',
            'title': 'test article',
            'message_text': 'Я пришел к тебе с приветом',
            'obj': {
                'name': 'Пушкин',
                'timezone': 1,
            }
        }
    }
    body = json.dumps(data)
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/answerWebAppQuery'

    r = requests.post(url, headers=headers, data=body)
    assert 200 == r.status_code
