import asyncio
import base64
import hashlib
import hmac
import re
from datetime import date
from operator import itemgetter
from urllib.parse import parse_qsl

from aiogram import Bot

from config import Config


def check_webapp_signature(token: str, init_data: str) -> bool:
    """
    Check incoming WebApp init data signature
    Source: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    :param token:
    :param init_data:
    :return:
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        # Init data is not a valid query string
        return False
    if "hash" not in parsed_data:
        # Hash is not present in init data
        return False

    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_


def decode_base64_str(base64_encoded: str):
    try:
        base64_bytes = base64_encoded.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded = message_bytes.decode('ascii')
    except Exception:
        decoded = ''
    return decoded


def re_search(pattern: str, txt: str) -> str | None:
    _match = re.search(pattern, txt)
    if _match:
        return _match[1]
    return None


def get_days_left(date_event: date) -> int:
    """
    Осталось дней от заданной даты до сегодня
    :param date_event:
    :return: число дней
    """
    today = date.today()
    days_left = (date_event - today).days
    return days_left


def is_number(txt: str) -> bool:
    if txt is None:
        return False
    return txt.isdigit()


def calc_payment_sum(count: int):
    if 1 <= count <= 5:
        return count * 250
    if 6 <= count <= 49:
        return count * 200
    if 50 <= count <= 99:
        return count * 150
    if count >= 100:
        return count * 100
    return 0


async def get_bot_url() -> str:
    token = Config().token
    bot = Bot(token)
    bot_me = await bot.get_me()
    bot_url = f'https://t.me/{bot_me.username}'
    return bot_url
