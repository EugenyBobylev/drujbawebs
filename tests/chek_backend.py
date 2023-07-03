import requests
from fastapi.encoders import jsonable_encoder

from backend import User, Fundraising

auth = 'cXVlcnlfaWQ9QUFISFNXc0hBQUFBQU1kSmF3ZUxNU0FiJnVzZXI9JTdCJTIyaWQlMjIlM0ExMjQ0NzE3NTElMkMlMjJmaXJzdF9uYW1' \
       'lJTIyJTNBJTIyJUQwJTk1JUQwJUIyJUQwJUIzJUQwJUI1JUQwJUJEJUQwJUI4JUQwJUI5JTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIy' \
       'JUQwJTkxJUQwJUJFJUQwJUIxJUQxJThCJUQwJUJCJUQwJUI1JUQwJUIyJTIyJTJDJTIydXNlcm5hbWUlMjIlM0ElMjJCb2J5bGV2RUElM' \
       'jIlMkMlMjJsYW5ndWFnZV9jb2RlJTIyJTNBJTIyZW4lMjIlN0QmYXV0aF9kYXRlPTE2ODMxOTQzMzUmaGFzaD0yOTJhNzhiZmNhNjY1ZT' \
       'EwNGQ5ZDRmMDEzN2QwNWQxMjU0NzE3Yzc4MjAxYWMzYmJkMzcwMWQwYWU3MzFhZWQz'


# *************************************
# Required working backend
# *************************************
base_url = 'http://127.0.0.1:8000'
# base_url = 'http://89.223.121.3:8000'


def check_get_root():
    url = f'{base_url}/'
    r = requests.get(url)
    assert r.status_code == 200


def check_create_user():
    url = f'{base_url}/user/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    user = User(id=1234, name='test_user', timezone=1, birthdate='1966-12-15')
    user_json = jsonable_encoder(user)
    r = requests.post(url, headers=headers, json=user_json)
    assert r.status_code == 200


def check_create_event():
    url = f'{base_url}/event/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }

    event_data = {
        'user_id': 1234,
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
        'invite_url': r'tme:/drujba/pe_0012'
    }
    event = Fundraising(**event_data)
    event_json = jsonable_encoder(event)

    r = requests.post(url, headers=headers, json=event_json)
    assert r.status_code == 200
    answer = r.json()
    print(answer)


if __name__ == '__main__':
    check_get_root()
    check_create_user()
    check_create_event()
