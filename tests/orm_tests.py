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


def test_insert_user():
    session = get_session()
    tgid = 124471751
    user_data = {
        'name': 'Егор Летов',
        'timezone': 3,
        'birthdate': '1966-12-15',
    }

    user = db.insert_user(user_id=tgid, session=session, **user_data)
    assert tgid == user.id
    assert 'Егор Летов' == user.name
    assert 3 == user.timezone
    assert '1966-12-15' == user.birthdate.strftime('%Y-%m-%d')


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
    assert '1967-12-15' == user.birthdate.strftime('%Y-%m-%d')


def test_delete_user():
    session = get_session()
    tgid = 124471751
    db.delete_user(tgid, session)

    user = db.get_user(tgid, session)
    assert user is None


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


# *********************************************
# Account
# *********************************************
def test_get_not_exists_account():
    account = db.get_account(account_id=-22)
    assert account is None


def test_insert_private_account():
    session = get_session()
    user = get_user()
    account = db.get_private_account(user.id, session)
    if account is None:
        account = db.insert_account(user.id, None, session, payed_events=1)

    assert account is not None
    assert 1 == account.payed_events
    assert user.id == account.owner.id
    assert user.name == account.owner.name


def test_insert_company_account():
    session = get_session()
    user = get_user()
    company = get_company_by_name()
    account = db.get_company_account(company.id, session)
    if account is None:
        account = db.insert_account(user.id, company.id, session, payed_events=0)

    assert account is not None
    assert 0 == account.payed_events
    assert user.id == account.owner.id
    assert user.name == account.owner.name
    assert company.id == account.company.id
    assert company.name == account.company.name


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
        'name': 'ProfiTeam',
        'industry': 'Software engineering',
        'person_count': 1,
    }
    company = db.insert_company(session, **data)
    assert company is not None
    assert 'ProfiTeam' == company.name
    assert 1 == company.person_count


def test_change_company_account_admin():
    session = get_session()
    company = get_company_by_name()
    account = db.get_company_account(company.id, session)
    old_admin = get_user(account.user_id)

    admin_id = 123 if old_admin.id == 124471751 else 124471751
    admin = get_user(admin_id)

    assert account is not None
    assert admin is not None

    account.user_id = admin.id
    session.commit()
    account = db.get_company_account(company.id, session)

    assert  account.user_id == admin.id


def get_company_by_name(name: str = 'ProfiTeam'):
    session = get_session()
    company = db.get_company_by_name(name, session)
    if company is None:
        data = {
            'name': name,
            'industry': 'Software engineering',
            'person_count': 1,
        }
        company = db.insert_company(session, **data)
    return company


# Эту херню надо протестить
def test_create_user():
    api_user = apiUser(id=123, name='Popov', birthdate='1980-02-10', timezone=1)
    assert api_user is not None

    user: User = db.create_user(api_user)
    assert user is not None
    assert 123 == user.id
    assert 'Popov' == user.name
