from datetime import date

from sqlalchemy import create_engine, select, func

from config import Config

import db
from db import get_session
from db.models import User, Account, Company


def test_connect_to_postgres():
    config = Config()
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
    assert count == 0


def test_get_not_exist_user():
    session = get_session()
    user1 = session.get(User, -1234)
    user2 = session.scalars(select(User).where(User.id == 1234)).first()

    assert user1 is None
    assert user2 is None


def test_insert_user():
    session = get_session()
    user_id = 1234
    user_data = {
        'name': 'Eugeny Bobylev',
        'timezone': 2,
        'birthdate': '1966-12-15'
    }
    user = User(id=user_id, **user_data)
    session.add(user)
    session.commit()

    assert True


def test_get_exist_user():
    session = get_session()
    user_id = 1234
    user1: User = session.get(User, user_id)
    user2 = session.scalars(select(User).where(User.id == 1234)).first()

    assert user1
    assert user1.id == 1234
    assert user1.name == 'Eugeny Bobylev'
    assert user1.birthdate == date(1966, 12, 15)

    assert user1 == user2


def test_update_user():
    session = get_session()
    user_id = 1234
    user: User = session.get(User, user_id)

    user.name = 'Maria Lyutova'
    user.birthdate = date(1969, 8, 10)
    session.commit()

    assert True

    query = select(User).where(User.id == user_id)
    user: User = session.execute(query).scalars().first()

    assert user
    assert user.id == 1234
    assert user.name == 'Maria Lyutova'
    assert user.birthdate == date(1969, 8, 10)


def test_delete_user():
    session = get_session()
    user_id = 1234

    user = session.get(User, 1234)

    session.delete(user)
    session.commit()

    user = session.get(User, 1234)
    assert user is None


def test_get_member():
    session = get_session()
    company = session.get(Company, 1)

    assert company is not None
    assert company.admin is not None
    assert company.admin.name == 'user_1'
    assert len(company.members) == 2

    user_1 = session.get(User, 1)
    assert user_1 is not None
    assert len(user_1.members) == 1
    assert user_1.members[0].company is not None
    assert user_1.members[0].company.name == company.name

    # отобрать компанию по ее наименованию в
    user_1_company: Company = [mc.company for mc in user_1.members if mc.company.name == company.name][0]
    assert user_1_company is not None and user_1_company.name == company.name

    user_2 = session.get(User, 2)
    assert user_2 is not None
    assert len(user_2.members) == 1
    assert user_2.members[0].company is not None
    assert user_2.members[0].company.name == company.name

    # Найти всех пользователей компании
    company_users = [mc.user for mc in company.members]
    assert len(company_users) == 2
    assert type(company_users[0]) == User


def test_users_count():
    session = get_session()
    count = session.scalar(
        select(func.count()).select_from(User).where(User.id < 10000)
    )
    # count = session.query(User).count()
    assert count == 3


def test_users_timezone_sum():
    session = get_session()
    total_sum = session.scalar(
        select(func.sum(User.timezone)).select_from(User).where(User.id < 10000)
    )

    assert total_sum == 6

