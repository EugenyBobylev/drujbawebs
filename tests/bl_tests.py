import json
from json import JSONDecodeError

from backend import User as apiUser, Fundraising
import db
from db import get_session, db_get_user_account, remove_user, UserStatus, get_user_statuses, create_fundraising
from db.models import User, Account
from db.repository import db_get_member_account, db_get_company, db_get_company_by_name, db_insert_company, \
    db_get_user, db_get_company_user, db_insert_company_user, db_update_company_user, db_delete_company_user, \
    db_get_fundraising, db_insert_user_account, db_insert_fundraising, db_get_company_account, db_get_fund_total_sum, \
    db_get_all_donor_count, db_register_user, init_texts_tbl, db_insert_user, db_update_user, db_is_user_registered, \
    db_delete_user, db_get_account, db_delete_account, db_update_account, db_get_user_all_accounts


# *********************************************
# User
# *********************************************
def test_get_not_exists_user():
    session = get_session()
    user_id = -12
    user = db_get_user(user_id, session)
    assert user is None


def test_insert_user():
    session = get_session()
    user_id = 124471751
    user_data = {
        'name': 'Егор Летов',
        'timezone': 3,
        'birthdate': '1966-12-15',
    }

    user: User = db_insert_user(user_id=user_id, session=session, **user_data)
    assert user_id == user.id
    assert 'Егор Летов' == user.name
    assert 3 == user.timezone
    assert '1966-12-15' == '1966-12-15'


def test_get_user():
    session = get_session()
    user_id = 124471751
    user = db_get_user(user_id, session)
    assert user is not None
    assert user_id == user.id


def test_update_user():
    session = get_session()
    user_id = 124471751
    user_data = {
        'name': 'Мария Лютова',
        'timezone': 1,
        'birthdate': '1967-12-15',
    }

    user = db_update_user(user_id, session, **user_data)
    assert 'Мария Лютова' == user.name
    assert 1 == user.timezone
    assert '1967-12-15' == user.birthdate


def test_is_user_not_registered():
    session = get_session()
    user_id = 124471751
    registered = db_is_user_registered(user_id, session)
    assert not registered


def test_delete_user():
    session = get_session()
    user_id = 22

    user = db_get_user(user_id, session)
    assert user is not None

    db_delete_user(user_id, session)

    user = db_get_user(user_id, session)
    assert user is None


def test_register_user():
    session = get_session()
    user_id = 124471751
    user_data = {
        'name': 'Егор Летов',
        'timezone': 3,
        'birthdate': '1966-12-15',
    }
    user = db_register_user(user_id, session, **user_data)
    assert user is not None


def test_is_user_registered():
    session = get_session()
    user_id = 124471751
    registered = db_is_user_registered(user_id, session)
    assert registered


def test_remove_user():
    user_id = 124471751
    remove_user(user_id)

    session = get_session()
    user = db_get_user(user_id, session)

    assert user is None


# *********************************************
# User and Company Account
# *********************************************
def test_get_not_exists_account():
    session = get_session()
    account = db_get_account(account_id=-22, session=session)
    assert account is None


def test_delete_company_account():
    session = get_session()
    company = get_company_by_name()
    account = db_get_company_account(company.id, session)
    if account:
        db_delete_account(account.id, session)
        account = db_get_company_account(company.id, session)

    assert account is None


def test_get_company_account():
    session = get_session()
    account = db_get_company_account(13, session)

    assert account is not None


def test_get_user_account():
    session = get_session()
    account = db_get_user_account(124471751, session)

    assert account is not None
    assert account.id == 33


def test_get_user_all_accounts():
    session = get_session()
    accounts = db_get_user_all_accounts(124471751, session)

    assert accounts is not None
    assert type(accounts) == list
    assert len(accounts) == 2


def test_get_member_account():
    session = get_session()
    account = db_get_member_account(14, 124471751, session)

    assert account is not None


# *********************************************
# Company
# *********************************************
def test_get_not_exists_company():
    session = get_session()
    company = db_get_company(company_id=-22, session=session)
    assert company is None


def test_get_not_exists_company_by_name():
    session = get_session()
    company = db_get_company_by_name('Рога и копыта-2', session=session)
    assert company is None


def test_insert_company():
    session = get_session()
    data = {
        'industry': 'Software engineering',
        'person_count': 1,
    }

    company = db_insert_company('Muvon', 124471751, session, **data)
    assert company is not None
    assert 'Muvon' == company.name
    assert 1 == company.person_count


def test_get_company_by_name():
    session = get_session()
    name = 'Muvon'
    company = db_get_company_by_name(name, session)

    assert company is not None


def test_create_user():
    api_user = apiUser(id=123, name='Popov', birthdate='1980-02-10', timezone=1)
    assert api_user is not None

    session = get_session()
    user = db_get_user(api_user.id, session)
    if user is None:
        user: User = db.create_user(api_user)

    assert user is not None
    assert 'Popov' == user.name


# *********************************************
# MC
# *********************************************
def test_get_mc():
    session = get_session()
    mc = db_get_company_user(100, 1, session)

    assert mc is not None
    assert mc.phone == '04'
    assert mc.email == 'santa@local'
    assert mc.title == 'Дед мороз'


def test_insert_exists_mc():
    session = get_session()
    data = {'phone': '03', 'email': 'qqq@host.my', 'title': 'Чебурашка'}
    mc = db_insert_company_user(100, 1, session, **data)

    assert mc is not None
    assert mc.phone == '04'
    assert mc.email == 'santa@local'
    assert mc.title == 'Дед мороз'


def test_insert_mc():
    session = get_session()
    data = {'phone': '03', 'email': 'qqq@host.my', 'title': 'Чебурашка'}
    mc = db_insert_company_user(124471751, 1, session, **data)

    assert mc is not None
    assert mc.phone == '03'
    assert mc.email == 'qqq@host.my'
    assert mc.title == 'Чебурашка'


def test_update_mc():
    session = get_session()
    data = {'phone': '03', 'email': 'qqq@host.my', 'title': 'Чебурашка'}
    mc = db_update_company_user(124471751, 1, session, **data)

    assert mc is not None
    assert mc.phone == '03'
    assert mc.email == 'qqq@host.my'
    assert mc.title == 'Чебурашка'


def test_delete_mc():
    session = get_session()
    mc = db_get_company_user(124471751, 1, session)

    # assert mc is not None
    db_delete_company_user(124471751, 1, session)
    mc = db_get_company_user(124471751, 1, session)
    assert mc is None


# *********************************************
# Fundraising
# *********************************************
def test_get_not_exist_fundraising():
    session = get_session()
    event_id = -100
    event = db_get_fundraising(event_id, session)

    assert event is None


def test_insert_company_fundraising():
    session = get_session()

    company = db_get_company_by_name('Muvon', session)
    assert company

    account = db_get_company_account(company.id, session)
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

    event = db_insert_fundraising(account.id, session, **event_data)
    assert event is not None


def test_total_sum_not_exist_fundraising():
    session = get_session()
    fund_id = -1234
    total_sum = db_get_fund_total_sum(fund_id, session)
    assert total_sum == 0


def test_donor_count_not_exist_fundraising():
    session = get_session()
    fund_id = -1234
    total_sum = db_get_all_donor_count(fund_id, session)
    assert total_sum == 0


def get_user(user_id: int = 124471751, name: str = 'Егор Летов') -> User:
    session = get_session()

    user_data = {
        'name': name,
        'timezone': 3,
        'birthdate': '1966-12-15',
    }
    user = db_register_user(user_id=user_id, session=session, **user_data)
    return user


def get_company_by_name(name: str = 'ProfiTeam'):
    session = get_session()
    user = get_user(1234, 'Иван Куев')
    company = db_get_company_by_name(name, session)
    if company is None:
        data = {
            'industry': 'Software engineering',
            'person_count': 1,
            'job_title': 'руководитель',
            'phone': '8-800-100=4455',
        }
        company = db_insert_company(name, user.id, session, **data)
    return company


def test_init_texts_tbl():
    session = get_session()
    init_texts_tbl(session)
    assert True


def test_get_current_tariff():
    account_id = 138
    tariff_name = db.get_current_tariff(account_id)
    assert tariff_name == 'Приятель'


def test_enum_to_str():
    assert UserStatus.User.name == 'User'


def test_get_visitor_status():
    user_id = 1

    session = get_session()
    user = db_get_user(user_id, session)
    if user:
        db_delete_user(user_id, session)

    statuses = get_user_statuses(user_id, False)

    assert type(statuses) == list
    assert len(statuses) == 1
    assert statuses[0].status == UserStatus.Visitor.name

    user = db_insert_user(user_id, session, name='test')
    if user:
        statuses = get_user_statuses(1, False)
        assert statuses[0].status == UserStatus.Visitor.name
        db_delete_user(user_id, session)

    # user_id = 124471751
    # status = db.get_user_status(user_id)
    # assert status == 'active'


def test_get_trialuser_status():
    user_id = 1

    session = get_session()
    user = db_get_user(user_id, session)
    if user is None:
        user = db_insert_user(user_id, session, name='test')
        account = db_insert_user_account(user.id, session)

    statuses = get_user_statuses(user_id, False)

    assert len(statuses) == 1
    assert statuses[0].status == UserStatus.TrialUser.name

    if user:
        db_delete_user(user_id, session)

    # user_id = 124471751
    # status = db.get_user_status(user_id)
    # assert status == 'active'


def test_unpack_gift_info():
    gift_info = '{"0":"https://21312312","1":"https://23221312312"}'
    gift_links = json.loads(gift_info)

    assert isinstance(gift_links, dict)
    print('\n')
    gift_links = '\n'.join(gift_links.values())
    print(gift_links)

    gift_info = 'На бухло и закуску'
    try:
        gift_links = json.loads(gift_info)
        gift_links = '\n'.join(gift_links.values())
    except JSONDecodeError:
        gift_links = gift_info
    assert isinstance(gift_links, str)


def test_create_fundraising():
    # я тестирую создание сбора при нулевом балансе, который надо подготовить до запуска теста
    fund = Fundraising(reason='Именины', target='У Кристиный',
                       account_id=96, event_date='2023-08-30', transfer_info='карта 5555-5555-5555-4444')
    result = create_fundraising(96, fund)

    assert result is not None
    assert result.id is not None
    assert result.start is None
    assert result.invite_url == ''
