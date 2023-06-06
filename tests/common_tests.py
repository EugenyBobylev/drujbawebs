import asyncio
import os
import random
import tempfile
import urllib
import uuid
from datetime import datetime, date
import json
from pathlib import Path

from backend.models import WebAppInitData, Fundraising
from chat.user_chat import async_create_chat2, async_create_chat, async_change_chats_owners
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


def test_read_all_files():
    path = os.path.abspath(__file__)
    work_dir = str(Path(path).parent)
    files = os.listdir(work_dir)
    files = [work_dir + '/' + f for f in files if os.path.isfile(work_dir + '/' + f) if f.endswith('.py')]

    assert len(files) > 0
    print(*files, sep="\n")


def test_add_lists():
    common_list = [0]
    other_list = [1,2,3,4]
    common_list = common_list + other_list

    assert len(common_list) == 5


def test_new_or_append():
    with open('temp.txt', mode='a+', encoding='utf-8') as f:
        f.write('first line\n')

    with open('temp.txt', mode='a+', encoding='utf-8') as f:
        f.write('second line\n')


def test_create_chat():
    chat_name='Тест'
    about = 'тестовый чат который нужно удалить после создания'
    chat_url = async_create_chat(chat_name, about)

    assert chat_url is not None
    assert len(chat_url) > 0

    with open('chats.txt', mode='a+', encoding='utf-8') as f:
        f.write(f'{chat_url}\n')


def test_create_api_fundraising():
    data = {
        'reason': 'День рождения',  # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
        'target': 'Семенычу',  # кому собираем
        'event_date': '2023-07-16',  # дата события
        'transfer_info': 'На карту Вадима Игоревича (3333-1144-3345-4444)',  # реквизиты перевода
        # 'gift_info': 'Какую-нибудь фигню для его авто, потом решим'
    }
    fund = Fundraising(**data)
    assert fund is not None


def test_fund_from_json():
    json_str = '{"reason": "qqq","target": "Www","event_date":"2023-07-12","transfer_info":"qwqwqwqw",' \
               '"gift_info": "", "congratulation_date": null,"congratulation_time": null,"event_place": "",' \
               '"event_dresscode": ""}'
    data = json.loads(json_str)
    fund = Fundraising(**data)

    assert type(data) == dict
    assert fund is not None
