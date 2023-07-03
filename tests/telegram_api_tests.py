import json

import requests
from telethon import TelegramClient, Button

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


async def send_payment_fail_msg(chat_id: int, account_id: int, payed_events: int):
    """
    Создать сообщение с кнопкой об ошибке при выполнении платежа
    :param chat_id:  пользователь
    :param account_id: номер аккаунта
    :param payed_events: количество оплаченных сборов
    :return:
    """
    config = Config()
    api_id = config.api_id
    api_hash = config.api_hash
    bot_token = config.test_token
    bot = TelegramClient('bot', api_id, api_hash)
    bot = bot.start(bot_token=bot_token)
    async with bot:
        _url = f'{config.base_url}payment/{account_id}/{payed_events}'
        _txt = f'К сожалению, оплата не прошла. Давайте попробуем ещё раз.'
        _keyboard = [
            Button.url('Оплатить', _url),
            Button.inline('В меню', 'go_menu')
        ]
        _msg = await bot.send_message(chat_id, _txt, buttons=_keyboard)
        assert _msg is not None
