from sqlalchemy import create_engine, Connection, select

from backend import User as apiUser
from config import BotConfig
from db.bl import get_session, insert_user, get_user, update_user, delete_user, create_user
from db.models import User


def test_connect_to_postgres():
    config = BotConfig.instance()
    url = config.get_postgres_url()
    engine = create_engine(url, pool_size=50, echo=False)
    assert engine is not None

    with engine.connect() as conn:
        assert conn is not None
        assert not conn.closed


def test_insert_user():
    session = get_session()
    tgid = 124471751
    user_data = {
        'name': 'Егор Летов',
        'timezone': 3,
        'birthdate': '1966-12-15',
    }

    user = insert_user(user_id=tgid, session=session, **user_data)
    assert tgid == user.id
    assert 'Егор Летов' == user.name
    assert 3 == user.timezone
    assert '1966-12-15' == user.birthdate.strftime('%Y-%m-%d')


def test_get_user():
    session = get_session()
    tgid = 124471751
    user = get_user(tgid, session)
    assert user is not None
    assert tgid == user.id


def test_get_not_exist_user():
    session = get_session()
    tgid = 12
    user = get_user(tgid, session)
    assert user is None


def test_update_user():
    session = get_session()
    tgid = 124471751
    user_data = {
        'name': 'Мария Лютова',
        'timezone': 1,
        'birthdate': '1967-12-15',
    }

    user = update_user(tgid, session, **user_data)
    assert 'Мария Лютова' == user.name
    assert 1 == user.timezone
    assert '1967-12-15' == user.birthdate.strftime('%Y-%m-%d')


def test_delete_user():
    session = get_session()
    tgid = 124471751
    delete_user(tgid, session)

    user = get_user(tgid, session)
    assert user is None


def test_create_user():
    api_user = apiUser(id=123, name='Popov', birthdate='1980-02-10', timezone=1)
    assert api_user is not None

    user: User = create_user(api_user)
    assert user is not None
    assert 123 == user.id
    assert 'Popov' == user.name
