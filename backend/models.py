import json
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, date, time

from pydantic import BaseModel

from utils import re_search, decode_base64_str


@dataclass
class WebAppUser:
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str

    def __repr__(self):
        return f'id={self.id}; first_name={self.first_name} last_name={self.last_name}; username={self.username}'


@dataclass
class WebAppInitData:
    query_id: str
    user: WebAppUser
    auth_date: datetime
    hash: str

    def __repr__(self):
        return f'query_id="{self.query_id}" user={self.user.username}; auth_date={self.auth_date}'

    @classmethod
    def from_init_str(cls, decoded_str: str) -> 'WebAppInitData | None':
        query_id = re_search('query_id=(.*?)&', decoded_str)
        if query_id is None:
            return None

        user_str = re_search('user=(.*?)&', decoded_str)
        if user_str is None:
            return None
        user_data = json.loads(user_str)
        user = WebAppUser(**user_data)
        if user is None:
            return None

        auth_date_str = re_search('auth_date=(.*?)&', decoded_str)
        if auth_date_str is None:
            return None
        auth_date = datetime.fromtimestamp(int(auth_date_str))

        _hash = re_search('hash=(.*)$', decoded_str)
        if hash is None:
            return None
        return cls(query_id=query_id, user=user, auth_date=auth_date, hash=_hash)

    @staticmethod
    def form_auth_header(authorization: str) -> 'WebAppInitData | None':
        decoded_str = decode_base64_str(authorization)
        init_data = urllib.parse.unquote(decoded_str)
        return WebAppInitData.from_init_str(init_data)


class User(BaseModel):
    id: int
    name: str
    birthdate: date = None
    timezone: int

    def __repr__(self):
        return f'id={self.id}; name={self.name}; timezone={self.timezone}; birthdate={self.birthdate}'


class Account(BaseModel):
    id: int
    user_id: int = None
    company_id: int = None
    payed_events: int


class Fundraising(BaseModel):
    user_id: int
    account_id: int = None
    event_id: int = None
    reason: str = ''          # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
    target: str               # кому собираем
    start: date = None        # дата регистрации сбора
    end: date = None          # дата окончания сбора
    event_date: date          # дата события
    transfer_info: str        # реквизиты перевода (номер карты или телефон)
    gift_info: str = ''       # варианты подарков
    congratulation_date: date = None  # дата праздничного мероприятия
    congratulation_time: time = None  # время праздничного мероприятия
    event_place: str = None           # место проведения мероприятия
    event_dresscode: str = ''  # дресс-код
    invite_url: str            # ссылка приглашения для участия в сборе
