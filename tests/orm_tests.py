from sqlalchemy import create_engine, select, func

from backend import User as apiUser
from config import BotConfig

import db
from db import get_session
from db.models import User, Account


def test_connect_to_postgres():
    config = BotConfig.instance()
    url = config.get_postgres_url()
    engine = create_engine(url, pool_size=50, echo=False)
    assert engine is not None

    with engine.connect() as conn:
        assert conn is not None
        assert not conn.closed


def test_count():
    session = get_session()
    count: int = session.scalar(
        select(func.count()).select_from(Account).where(Account.user_id == 15)
    )
    assert 0 == count


# *********************************************
# Account
# *********************************************
def test_insert_user():
    session = get_session()
    tgid = 124471751
    user_data = {
        'name': 'Егор Летов',
        'timezone': 3,
        'birthdate': '1966-12-15',
    }

    user: User = db.insert_user(user_id=tgid, session=session, **user_data)
    assert tgid == user.id
    assert 'Егор Летов' == user.name
    assert 3 == user.timezone
    assert '1966-12-15' == '1966-12-15'


def test_get_user():
    session = get_session()
    tgid = 124471751
    user = db.get_user(tgid, session)
    assert user is not None
    assert tgid == user.id


def test_get_not_exists_user():
    session = get_session()
    tgid = 12
    user = db.get_user(tgid, session)
    assert user is None


def test_update_user():
    session = get_session()
    tgid = 124471751
    user_data = {
        'name': 'Мария Лютова',
        'timezone': 1,
        'birthdate': '1967-12-15',
    }

    user = db.update_user(tgid, session, **user_data)
    assert 'Мария Лютова' == user.name
    assert 1 == user.timezone
    assert '1967-12-15' == user.birthdate


def test_delete_user():
    session = get_session()
    tgid = 124471751
    db.delete_user(tgid, session)

    user = db.get_user(tgid, session)
    assert user is None


# *********************************************
# Account
# *********************************************
def test_get_not_exists_account():
    session = get_session()
    account = db.get_account(account_id=-22, session=session )
    assert account is None


def test_insert_private_account():
    session = get_session()
    user = get_user()
    account = db.get_private_account(user.id, session)
    if account is None:
        account = db.insert_account(user.id, session, payed_events=1)

    assert account is not None
    assert 1 == account.payed_events
    assert user.id == account.owner.id
    assert user.name == account.owner.name


def test_get_private_account():
    session = get_session()
    user = get_user()
    account = db.get_private_account(user.id, session)

    assert account is not None
    assert 1 == account.payed_events


def test_update_account():
    session = get_session()
    user = get_user()
    account = db.get_private_account(user.id, session)
    account = db.update_account(account.id, session, payed_events=10)

    assert 10 == account.payed_events


def test_delete_private_account():
    session = get_session()
    user = get_user()
    account = db.get_private_account(user.id, session)
    if account:
        db.delete_account(account.id, session)
        account = db.get_private_account(user.id, session)

    assert account is None


def test_delete_company_account():
    session = get_session()
    company = get_company_by_name()
    account = db.get_company_account(company.id, session)
    if account:
        db.delete_account(account.id, session)
        account = db.get_company_account(company.id, session)

    assert account is None


# *********************************************
# Company
# *********************************************
def test_get_not_exists_company():
    session = get_session()
    company = db.get_company(company_id=-22, session=session)
    assert company is None


def test_get_not_exists_company_by_name():
    session = get_session()
    company = db.get_company_by_name('Рога и копыта-2', session=session)
    assert company is None


def test_get_company_by_name():
    session = get_session()
    name = 'ProfiTeam'
    company = db.get_company_by_name(name, session)

    assert company is not None


def test_insert_company():
    session = get_session()
    data = {
        'industry': 'Software engineering',
        'person_count': 1,
        'job_title': 'инженер',
        'email': 'qqq@test.com',
        'phone': '+7 918-376-1876'
    }

    company = db.insert_company('Muvon', 124471751, session, **data)
    assert company is not None
    assert 'Muvon' == company.name
    assert 1 == company.person_count


def test_get_members():
    session = get_session()
    company = get_company_by_name()
    result = db.get_members(company.id, session)
    assert len(result) > 0


def test_create_user():
    api_user = apiUser(id=123, name='Popov', birthdate='1980-02-10', timezone=1)
    assert api_user is not None

    session = get_session()
    user = db.get_user(api_user.id, session)
    if user is None:
        user: User = db.create_user(api_user)
    assert user is not None
    assert 'Popov' == user.name


# *********************************************
# Fundraising
# *********************************************
def test_get_not_exist_fundraising():
    session = get_session()
    event_id = -100
    event = db.get_fundraising(event_id, session)

    assert event is None


def test_insert_private_fundraising():
    session = get_session()
    user = get_user(124471751)
    account = db.get_private_account(user.id, session)
    if account is None:
        account = db.insert_account(user.id, session)
    assert account is not None

    event_data = {
        'reason': 'ДР',
        'target': 'юбилей',
        'start': '2023-01-15',
        'end': '2023-05-10',
        'event_date': '2023-05-15',
        'transfer_info': 'на карту Мир сбербанка 000-1111-2222-4444',
        'gift_info': 'ящик коньяка',
        'congratulation_date': '2023-05-16',
        'congratulation_time': '19:00',
        'event_place': 'Дача юбиляра на Щукинке',
        'event_dresscode': 'чтобы комары на сожрали',
        'invite_url': r'tme:/drujba/pe_0012'
    }

    event = db.insert_fundraising(account.id, session, **event_data)
    assert event is not None


def test_insert_company_fundraising():
    session = get_session()

    company = db.get_company_by_name('ProfiTeam', session)
    assert company

    account = db.get_company_account(company.id, session)
    assert account

    event_data = {
        'reason': 'Новый год',
        'target': 'корпоратив в ресторане',
        'start': '2023-04-10',
        'end': '2023-12-20',
        'event_date': '2023-12-28',
        'transfer_info': 'на карту Мир сбербанка 000-1111-2222-4444',
        'gift_info': 'ящик коньяка + ящик шампанского, + ящик водки',
        'congratulation_date': '2023-12-29',
        'congratulation_time': '19:00',
        'event_place': 'ресторан Поплавок',
        'event_dresscode': 'в карнавльных костюмах + маски',
        'invite_url': r'tme:/drujba/pe_0015'
    }

    event = db.insert_fundraising(account.id, session, **event_data)
    assert event is not None


def get_user(user_id: int = 124471751, name: str = 'Егор Летов') -> User:
    session = get_session()

    user = db.get_user(user_id, session)
    if not user:
        user_data = {
            'name': name,
            'timezone': 3,
            'birthdate': '1966-12-15',
        }
        user = db.insert_user(user_id=user_id, session=session, **user_data)
    return user


def get_company_by_name(name: str = 'ProfiTeam'):
    session = get_session()
    user = get_user(1234, 'Иван Куев')
    company = db.get_company_by_name(name, session)
    if company is None:
        data = {
            'industry': 'Software engineering',
            'person_count': 1,
            'job_title': 'руководитель',
            'phone': '8-800-100=4455',
        }
        company = db.insert_company(name, user.id, session, **data)
    return company
