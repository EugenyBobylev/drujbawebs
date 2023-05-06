import urllib
from datetime import datetime
import json

from backend.model import WebAppInitData
from config import BotConfig
from utils import re_search, check_webapp_signature, decode_base64_str
import urllib.parse

auth = 'cXVlcnlfaWQ9QUFISFNXc0hBQUFBQU1kSmF3ZUxNU0FiJnVzZXI9JTdCJTIyaWQlMjIlM0ExMjQ0NzE3NTElMkMlMjJmaXJzdF9uYW1' \
       'lJTIyJTNBJTIyJUQwJTk1JUQwJUIyJUQwJUIzJUQwJUI1JUQwJUJEJUQwJUI4JUQwJUI5JTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIy' \
       'JUQwJTkxJUQwJUJFJUQwJUIxJUQxJThCJUQwJUJCJUQwJUI1JUQwJUIyJTIyJTJDJTIydXNlcm5hbWUlMjIlM0ElMjJCb2J5bGV2RUElM' \
       'jIlMkMlMjJsYW5ndWFnZV9jb2RlJTIyJTNBJTIyZW4lMjIlN0QmYXV0aF9kYXRlPTE2ODMxOTQzMzUmaGFzaD0yOTJhNzhiZmNhNjY1ZT' \
       'EwNGQ5ZDRmMDEzN2QwNWQxMjU0NzE3Yzc4MjAxYWMzYmJkMzcwMWQwYWU3MzFhZWQz'

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
    config = BotConfig.instance()
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
    config = BotConfig.instance()
    ok = check_webapp_signature(config.token, init_data)
    assert ok
