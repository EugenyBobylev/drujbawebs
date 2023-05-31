import json

import requests

from config import Config


def test_post_simple_message():
    token = Config().test_token
    chat_id = 124471751
    message = 'Привет. Это текстовое сообщение'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'chat_id': chat_id,
        'text': message
    }
    body = json.dumps(data)
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    r = requests.post(url, headers=headers, data=body)
    assert r.status_code == 200


def test_post_msg_with_url_buttons():
    token = Config().test_token
    chat_id = 124471751
    message = 'Привет. Нажми на кнопку и перейди на внешний сайт и не только...'
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {'text': 'go to python.org', 'url': 'https://python.org'},
                    {'text': 'В меню', 'callback_data': 'go_menu'}

                ]
            ]
        }
    }

    body = json.dumps(data)
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    r = requests.post(url, headers=headers, data=body)
    assert r.status_code == 200
