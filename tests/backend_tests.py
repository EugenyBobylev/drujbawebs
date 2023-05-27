import json

import requests
from fastapi.encoders import jsonable_encoder

from backend import User
from backend import send_message
from backend.models import PaymentResult
from config import BotConfig
from db import Account

auth = 'cXVlcnlfaWQ9QUFISFNXc0hBQUFBQU1kSmF3ZUxNU0FiJnVzZXI9JTdCJTIyaWQlMjIlM0ExMjQ0NzE3NTElMkMlMjJmaXJzdF9uYW1' \
       'lJTIyJTNBJTIyJUQwJTk1JUQwJUIyJUQwJUIzJUQwJUI1JUQwJUJEJUQwJUI4JUQwJUI5JTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIy' \
       'JUQwJTkxJUQwJUJFJUQwJUIxJUQxJThCJUQwJUJCJUQwJUI1JUQwJUIyJTIyJTJDJTIydXNlcm5hbWUlMjIlM0ElMjJCb2J5bGV2RUElM' \
       'jIlMkMlMjJsYW5ndWFnZV9jb2RlJTIyJTNBJTIyZW4lMjIlN0QmYXV0aF9kYXRlPTE2ODMxOTQzMzUmaGFzaD0yOTJhNzhiZmNhNjY1ZT' \
       'EwNGQ5ZDRmMDEzN2QwNWQxMjU0NzE3Yzc4MjAxYWMzYmJkMzcwMWQwYWU3MzFhZWQz'


# *************************************
# Required working backend
# *************************************
def test_get_root():
    url = 'http://127.0.0.1:8000/'
    headers = {
        'Authorization': auth
    }
    r = requests.get(url)
    assert r.status_code == 200


def test_create_user_without_auth():
    url = 'http://127.0.0.1:8000/user/'
    user = User(id=1234, name='test_user', timezone=1, birthdate='1980-01-23')
    user_json = jsonable_encoder(user)
    r = requests.post(url, json=user_json)
    assert r.status_code == 422


def test_create_user_with_auth():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    user = User(id=1234, name='Kent Beck', timezone=1, birthdate='1960-01-23')
    user_json = jsonable_encoder(user)
    r = requests.post(url, headers=headers, json=user_json)
    assert r.status_code == 200


def test_get_user():
    url = 'http://127.0.0.1:8000/user/1234/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    r = requests.get(url, headers=headers)
    api_user: Account = r.json()
    assert r.status_code == 200
    assert api_user is not None


def test_get_wrong_user():
    url = 'http://127.0.0.1:8000/user/-1234/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    r = requests.get(url, headers=headers)
    assert r.status_code == 204


def test_get_user_account():
    url = 'http://127.0.0.1:8000/user/account/1234/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    r = requests.get(url, headers=headers)
    api_model: Account = r.json()
    assert r.status_code == 200


def test_get_wrong_user_account():
    url = 'http://127.0.0.1:8000/user/account/-1234/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    r = requests.get(url, headers=headers)
    assert r.status_code == 204


def test_create_user_fundraising():
    user_id = 1234
    url = f'http://127.0.0.1:8000/user/fundraising/{user_id}/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    fund = {
        'reason': 'ДР',
        'target': 'юбилей',
        'start': '2023-01-15',
        'end': '2023-05-10',
        'event_date': '2023-05-15',
        'transfer_info': 'на карту Мир сбербанка 000-1111-2222-4444',
        'gift_info': 'ящик коньяка',
        'congratulation_date': '2023-05-16',
        'congratulation_time': '19:00',
        'event_place': 'Дача юбиляра на Щукинке',
        'event_dresscode': 'чтобы комары на сожрали',
    }

    fund_json = jsonable_encoder(fund)
    r = requests.post(url, headers=headers, json=fund_json)
    assert r.status_code == 200


# def test_create_user_with_wrong_auth():
#     url = 'http://127.0.0.1:8000/user/'
#     headers = {
#         'Authorization': 'all nonsense'
#     }
#     user = User(name='test_user', timezone=1)
#     r = requests.post(url, headers=headers, json=user.__dict__)
#     assert r.status_code == 401


def test_api_bot_send_me():
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/getMe'
    r = requests.get(url)
    assert 200 == r.status_code
    answer = r.json()
    assert answer['ok']
    assert 'conceptui' == answer['result']['first_name']
    assert 'conceptuibot' == answer['result']['username']


def test_answer_web_app_query():
    """
    Тест на отправку боту данных из WebApp
    перед выполнением, каждый раз, требуется обновлять web_query_id
    т.к. он может быть использован только единожды
    :return:
    """
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


def test_send_message():
    chat_id = 124471751
    text = 'Текстовое сообщение для примера'

    r = send_message(chat_id, text)
    assert 200 == r.status_code


def test_create_payment_result():
    data = {
        'code': 0,
        'success': True,
        'message': None,
        'account_id': 100,
        'cnt': 10,
        'transaction_id': None
    }
    res = PaymentResult(** data)
    assert res is not None
