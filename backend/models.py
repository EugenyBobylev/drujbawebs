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


class UserInfo(BaseModel):
    donors_count: int = 0   # участвует в сборах
    funds_count: int = 0    # создано сборов
    company_count: int = 0  # участвуете в компаниях
    open_funds: int = 0     # открытые сборы
    admin_count: int = 0    # администратор компаний


class CompanyUser(BaseModel):
    """
    создается при регистрации компании
    """
    company_name: str       # название компании
    activity: str           # сферадеятельности
    person_count: int       # количество человек в компании
    user_id: int            # id пользователя, совпадает с id телеграм пользователя
    user_name: str          # имя и фамилия
    birthdate: date         # день рождения
    timezone: int           # часовой пояс
    job: str                # должность
    phone: str              # телефон
    email: str              # адрес электронной почты


class Account(BaseModel):
    id: int
    user_id: int = None
    company_id: int = None
    payed_events: int


class Fundraising(BaseModel):
    id: int = None
    reason: str               # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
    target: str               # кому собираем
    account_id: int = None    # с какого аккаунта был создан сбор
    start: date = None        # дата регистрации сбора
    end: date = None          # дата окончания сбора
    event_date: date          # дата события
    transfer_info: str        # реквизиты перевода (номер карты или телефон)
    gift_info: str = ''       # варианты подарков
    congratulation_date: date = None  # дата праздничного мероприятия
    congratulation_time: time = None  # время праздничного мероприятия
    event_place: str = None           # место проведения мероприятия
    event_dresscode: str = ''  # дресс-код
    invite_url: str = ''       # ссылка приглашения для участия в сборе
    chat_url: str = ''         # ссылка на чат

    @classmethod
    def get_empty(cls):
        return cls(reason='', target='', event_date = date.today(), transfer_info='')


class FundraisingInfo(BaseModel):
    id: int = None
    is_open: bool = None
    is_ok: bool = None
    reason: str = ''          # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
    target: str = ''          # кому собираем
    event_date: date = None     # дата события
    days_left: int = None       # осталось дней до даты события (если < 0), то прошло дней
    donor_count: int = None     # количество людей присоединившихся к событию
    payed_count: int = None     # кол. людей сдавших деньги
    total_sum: int = None       # всего собрано денег
    avg_sum: float = None       # средний чек
    invite_url: str = ''        # ссылка на сбор

    def __repr__(self):
        return f'id={self.id}; is_open={self.is_open}; reason="{self.reason}"; target="{self.target}"; ' \
               f'event_date={self.event_date}; days_left={self.days_left}; donor_count={self.donor_count}; ' \
               f'total_sum={self.total_sum}; avg_sum={self.avg_sum}'

    def msg(self):
        is_open = 'ДА' if self.is_open else 'НЕТ'
        is_ok = 'да' if self.is_ok else 'нет'

        return f'Сбор открыт: {is_open}\n\nТип события: {self.reason}\nНа кого: {self.target}\n' \
               f'Дата: {self.event_date}\nОсталось дней: {self.days_left}\n\nСбор успешен: {is_ok}\n ' \
               f'Участники сбора: {self.donor_count} чел.\n\nСдали деньги: {self.payed_count} чел.\n' \
               f'Сумма сбора: {self.total_sum} руб.\nСредний чек: {self.avg_sum} руб.'


class FundraisingSmallInfo(BaseModel):
    id: int = None            # используется для передачи в feeHistory3.html
    target: str = ''          # кому собираем
    event_date: str = None    # дата события в виде строки вида "dd.mm.yyyy"
    is_open: bool = True      # открыт или закрыт сбор
    is_success: bool = True   # успешный или неуспешный сбор


class Donor(BaseModel):
    fund_id: int
    user_id: int
    name: str = ''
    payed_date: date = None
    payed: int = 0

    def __repr__(self):
        return f'find_id={self.fund_id}; user_id={self.user_id}; name="{self.name}"; payed={self.payed};' \
               f'payed_date={self.payed_date}'


class PaymentResult(BaseModel):
    code: int
    success: bool
    message: str = None
    account_id: int
    payed_events: int
    payed_sum: int
    transaction_id: int = None

    def __repr__(self):
        return f'code={self.code}; success={self.success}; message={self.message}; account_id={self.account_id}, ' \
               f'cnt={self.payed_events}; transaction_id={self.transaction_id}'
