import json

import requests
from requests import Response

from config import BotConfig


def send_answer_web_app_query(web_query_id: str, bot_obj: dict, title: str = '', message: str = '') -> Response:
    headers = {
        'Content-Type': 'application/json'
    }
    if title == '':
        title = f'article {web_query_id}'
    if message == '':
        message = 'response form WebApp'
    data = {
        'web_app_query_id': web_query_id,
        'result': {
            'type': 'article',
            'id': web_query_id,
            'title': title,
            'message_text': message,
            'obj': bot_obj
        }
    }
    body = json.dumps(data)
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/answerWebAppQuery'

    r = requests.post(url, headers=headers, data=body)
    return r
