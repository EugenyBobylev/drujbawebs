import json

import requests
from requests import Response

from config import Config


def send_answer_web_app_query(web_query_id: str, data: str) -> Response:
    token = Config().token
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'web_app_query_id': web_query_id,
        'result': {
            'type': 'article',
            'id': 112244,
            'title': 'Result',
            'input_message_content': {
                'message_text': f'webapp&{data}'
            }
        }
    }
    url = f'https://api.telegram.org/bot{token}/answerWebAppQuery'
    body = json.dumps(data)
    r = requests.post(url, headers=headers, data=body)
    return r


def send_message(chat_id: int, message: str) -> Response:
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'chat_id': chat_id,
        'text': message
    }
    body = json.dumps(data)
    token = Config().token
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    r = requests.post(url, headers=headers, data=body)
    return r
