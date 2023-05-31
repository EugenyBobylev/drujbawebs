import asyncio
import json

import aiohttp
import requests
from requests import Response

from backend import PaymentResult
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

#
# async def send_payment_fail_msg(chat_id: int, account_id: int, payed_events: int):
#     """
#     Создать сообщение с кнопкой об ошибке при выполнении платежа
#     :param chat_id:  пользователь
#     :param account_id: номер аккаунта
#     :param payed_events: количество оплаченных сборов
#     :return:
#     """
#     config = Config()
#     api_id = config.api_id
#     api_hash = config.api_hash
#     bot_token = config.token
#     bot = TelegramClient('bot', api_id, api_hash)
#     bot = await bot.start(bot_token=bot_token)
#     async with bot:
#         _url = f'{config.base_url}payment/{account_id}/{payed_events}'
#         _txt = f'К сожалению, оплата не прошла. Давайте попробуем ещё раз.'
#         _keyboard = [
#             Button.url('Оплатить', _url),
#             Button.inline('В меню', 'go_menu')
#         ]
#         _msg = await bot.send_message(chat_id, _txt, buttons=_keyboard)
#         assert _msg is not None
#


async def send_payment_fail_msg(chat_id: int, account_id: int, payed_events: int):
    """
    Создать сообщение с кнопкой об ошибке при выполнении платежа
    :param chat_id:  пользователь
    :param account_id: номер аккаунта
    :param payed_events: количество оплаченных сборов
    :return:
    """
    config = Config()
    token = config.token
    _url = f'{config.base_url}payment/{account_id}/{payed_events}'
    _txt = f'К сожалению, оплата не прошла. Давайте попробуем ещё раз.'
    data = {
        "chat_id": chat_id,
        "text": _txt,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {'text': 'Оплатить', 'url': _url},
                    {'text': 'В меню', 'callback_data': 'go_menu'}

                ]
            ]
        }
    }

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as r:
            code = r.status
            assert code == 200


async def send_payment_ok_msg(chat_id: int, payed_events: int):
    """
    Создать сообщение с кнопкой об успешном платеже
    :param chat_id:  пользователь
    :param payed_events: количество оплаченных сборов
    :return:
    """
    token = Config().token
    _txt = f'Поздравляю! Вы успешно приобрели пакет из: {payed_events} сборов. ' \
           'Теперь можно начинать готовиться к праздникам :)\n\nСпасибо, что выбрали Дружбу!'
    data = {
        "chat_id": chat_id,
        "text": _txt,
        "reply_markup": {
            "inline_keyboard": [
                [
                    # {'text': 'go to python.org', 'url': 'https://python.org'},
                    {'text': 'В меню', 'callback_data': 'go_menu'}

                ]
            ]
        }
    }

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as r:
            code = r.status
            assert code == 200


def send_payment_message(chat_id: int, result: PaymentResult):
    """
    Отправить пользователю в чат сообщение о результатах платежа
    """
    if result.success:
        asyncio.run(send_payment_ok_msg(chat_id, result.payed_events))
    else:
        asyncio.run(send_payment_fail_msg(chat_id, result.account_id, result.payed_events))
