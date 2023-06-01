import asyncio
import os
import urllib
from datetime import datetime, date
import json
from pathlib import Path

from backend.models import WebAppInitData
from config import Config
from utils import re_search, check_webapp_signature, decode_base64_str, get_bot_url
import urllib.parse

decoded_auth = 'query_id=AAHHSWsHAAAAAMdJawcUaqMP' \
               '&user=%7B%22id%22%3A124471751%2C%22' \
               'first_name%22%3A%22%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B9%22%2C%22' \
               'last_name%22%3A%22%D0%91%D0%BE%D0%B1%D1%8B%D0%BB%D0%B5%D0%B2%22%2C%22' \
               'username%22%3A%22BobylevEA%22%2C%22' \
               'language_code%22%3A%22en%22%7D' \
               '&auth_date=1683101106' \
               '&hash=c19a08a87aaafd17b1d2074f3c9b53051ad71873bc96f4ba370ae356755392fc'


def get_webapp_init_data() -> str:
    s = 'query_id=AAHHSWsHAAAAAMdJawcUaqMP' \
        '&user={"id":124471751,"first_name":"Евгений","last_name":"Бобылев","username":"BobylevEA",' \
        '"language_code":"en"}' \
        '&auth_date=1683101106' \
        '&hash=c19a08a87aaafd17b1d2074f3c9b53051ad71873bc96f4ba370ae356755392fc'
    return s


def test_create_config():
    config = Config()
    assert config is not None
    assert config.token is not None
    assert config.payment_username is not None
    assert config.payment_password is not None
    assert config.db is not None
    assert config.db_user is not None
    assert config.db_password is not None


def test_decode_webapp_init_data():
    base64_encoded = 'SGVsbG8gV29ybGQh'
    decoded = decode_base64_str(base64_encoded)
    assert 'Hello World!' == decoded, 'Результат не правильный!'


def test_parse_webapp_init_data():
    srs_str = get_webapp_init_data()
    decoded_str = urllib.parse.unquote(decoded_auth)
    assert srs_str == decoded_str

    query_id = re_search('query_id=(.*?)&', decoded_str)
    assert 'AAHHSWsHAAAAAMdJawcUaqMP' == query_id

    user_str = re_search('user=(.*?)&', decoded_str)
    user = json.loads(user_str)
    assert type(user) == dict

    auth_date_str = re_search('auth_date=(.*?)&', decoded_str)
    assert '1683101106' == auth_date_str
    auth_date = datetime.fromtimestamp(int(auth_date_str))
    assert datetime(2023, 5, 3, 11, 5, 6) == auth_date

    _hash = re_search('hash=(.*)$', decoded_str)
    assert 'c19a08a87aaafd17b1d2074f3c9b53051ad71873bc96f4ba370ae356755392fc' == _hash

    web_app_init_data: WebAppInitData = WebAppInitData.from_init_str(decoded_str)
    assert web_app_init_data is not None


def test_check_init_data_hash():
    init_data = urllib.parse.unquote(decoded_auth)
    config = Config()
    ok = check_webapp_signature(config.token, init_data)
    assert ok


def test_days_left():
    date_event = date(2023, 12, 15)
    today = date.today()
    days_left = (date_event - today).days
    print(f'\n{days_left=}')
    assert days_left > 0


def test_loguru():
    from loguru import logger
    # config log path
    app_dir = Config().app_dir
    logs_dir = Config().logs_dir
    log_path = f'{app_dir}/{logs_dir}/test.log'
    # remove exists log
    if Path(log_path).exists():
        os.remove(log_path)
    # config loguru
    logger.remove(0)
    logger.add(log_path)

    logger.debug("Happy logging with Loguru!")
    logger.info('Новое сообщение в лог')

    assert Path(log_path).exists()


def test_get_bot_url():
    url = asyncio.run(get_bot_url())
    assert url is not None
    assert url == f'https://t.me/conceptuibot'
