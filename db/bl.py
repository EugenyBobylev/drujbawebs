import asyncio
from datetime import date, timedelta
from enum import Enum

from sqlalchemy import create_engine, Engine, select, func
from sqlalchemy.orm import sessionmaker, Session

from backend import User as ApiUser, FundraisingInfo
from backend import Fundraising as ApiFundraising
from backend import Account as ApiAccount
from backend import Donor as ApiDonor
from backend import UserInfo as ApiUserInfo
from backend import PaymentResult as ApiPaymentResult
from config import Config
from db.models import Msg, User, Company, Account, Fundraising, Donor, Payment
from utils import get_days_left, get_bot_url


def get_engine() -> Engine:
    config = Config()
    url = config.get_postgres_url()
    engine = create_engine(url, pool_size=50, echo=False)
    return engine


def get_session(eng: Engine = None) -> Session:
    if eng is None:
        eng = get_engine()
    _Session = sessionmaker(bind=eng)
    session = _Session()
    session.expire_on_commit = False
    return session


def get_msg(text_name: str, session: Session) -> Msg | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(Msg).where(Msg.text_name == text_name)
    result = session.execute(query).scalars().first()
    return result


def _insert_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        msg = _update_msg(text_name, text_value, session)
    else:
        msg = Msg(text_name=text_name, text_value=text_value)
        session.add(msg)
        session.commit()
    return msg


def _update_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        msg.text_value = text_value
        session.commit()
    else:
        msg = _insert_msg(text_name, text_value, session)
    return msg


def _delete_msg(text_name: str, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        session.delete(msg)
        session.commit()


# **********************************************************************
#  User
# **********************************************************************
def _get_user(user_id: int, session: Session) -> User | None:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    return user


def _insert_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user:
        return user
    else:
        user = User(id=user_id)
        for field in User.get_fields():
            if field in kvargs:
                setattr(user, field, kvargs[field])
        session.add(user)
        session.commit()
    return user


def _update_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user is None:
        user = _insert_user(user_id, session, **kvargs)
    else:
        for field in User.get_fields():
            if field in kvargs:
                setattr(user, field, kvargs[field])
        session.commit()
    return user


def _delete_user(user_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()


def _register_user(user_id: int, session: Session, **kvargs) -> User:
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    user = session.get(User, user_id)
    if user:
        user = _update_user(user_id, session, **kvargs)
        account = _get_user_account(user_id, session)
        if account is None:
            _insert_user_account(user.id, session)
        session.refresh(user)
        return user

    user = _insert_user(user_id, session, **kvargs)
    account = _insert_user_account(user.id, session)
    assert account is not None
    return user


def _is_user_registered(user_id: int, session: Session) -> bool:
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user is not None:
        return user.account is not None
    return False


def _get_user_companies(user_id: int, session: Session) -> [Company]:
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    user_companies = []
    user = session.get(User, user_id)
    if user is not None:
        user_companies = [mc.company for mc in user.members]
    return user_companies


# **********************************************************************
# Account
# **********************************************************************
def _get_account(account_id: int, session: Session = None) -> Account | None:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.get(Account, account_id)
    return account


def _get_user_account(user_id: int, session: Session = None) -> Account | None:
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(Account).where(Account.user_id == user_id)).first()
    return account


def _get_company_account(company_id: int, session: Session = None) -> Account | None:
    if company_id is None:
        raise ValueError('company_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(Account).where(Account.company_id == company_id)).first()
    return account


def _insert_user_account(user_id: int, session: Session) -> Account:
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(Account).where(Account.user_id == user_id)).first()
    if account is not None:
        return account

    account = Account(user_id=user_id, payed_events=1)
    session.add(account)
    session.commit()
    return account


def _insert_company_account(company_id: int, session: Session) -> Account:
    if company_id is None:
        raise ValueError('company_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(User).where(Account.company_id == company_id)).first()
    if account is not None:
        return account

    account = Account(company_id=company_id, payed_events=0)
    session.add(account)
    session.commit()
    return account


def _update_account(account_id: int, session: Session, **kvargs) -> Account:
    if session is None:
        session = get_session()
    account = _get_account(account_id, session)
    kvargs.pop('user_id', None)
    kvargs.pop('company_id', None)

    for field in Account.get_fields():
        if field in kvargs:
            setattr(account, field, kvargs[field])
    session.commit()
    return account


def _delete_account(account_id: int, session: Session):
    if session is None:
        session = get_session()
    account = session.get(Account, account_id)
    if account is None:
        return
    session.delete(account)
    session.commit()


# **********************************************************************
# Company
# **********************************************************************
def _get_company(company_id: int, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    company = session.get(Company, company_id)
    return company


def _get_company_by_name(name: str, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    company = session.scalars(select(Company).where(Company.name == name)).first()
    return company


def _insert_company(name: str, admin_id: int, session: Session, **kvargs) -> Company:
    if name is None:
        raise ValueError("name can't be None")
    if admin_id is None:
        raise ValueError("admin_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    company = _get_company_by_name(name, session)
    if company:
        company.admin_id = admin_id
        _update_company(company.id, session, **kvargs)

    company = Company(name=name, admin_id=admin_id)
    for field in Company.get_fields():
        if field in kvargs:
            setattr(company, field, kvargs[field])
    session.add(company)
    session.commit()

    # сразу создать account
    _insert_company_account(company.id, session)
    session.commit()
    return company


def _update_company(company_id: int, session: Session, **kvargs) -> Company:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    company = session.get(Company, company_id)
    if company is None:
        raise ValueError("company_id not found")

    fields = Company.get_fields()
    for field in fields:
        if field in kvargs:
            setattr(company, field, kvargs[field])
    session.commit()
    return company


def _delete_company(company_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    company = session.get(Company, company_id)
    if company:
        session.delete(company)
        session.commit()


def _get_company_users(company_id: int, session: Session) -> [User]:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    company_users = []
    company = session.get(Company, company_id)
    if company is not None:
        company_users = [mc.user for mc in company.members]
    return company_users


def _get_member(company_id: str, user_id: int, session: Session) -> [Account]:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    query = select(Account).where(Account.company_id == company_id).where(Account.user_id == user_id)
    result = session.execute(query).scalars().all()
    return result


def _add_member(company_id: int, user_id: int, session: Session, **kvargs) -> Account:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    account = _get_member(company_id, user_id, session)
    if account is not None:
        _update_account(account.id, session, **kvargs)
        return account

    account = _insert_user_account(user_id, session)
    account.company_id = company_id
    session.commit()
    return account


# **********************************************************************
# Fundraising
# **********************************************************************
def _get_fundraising(fund_id: int, session: Session) -> Fundraising | None:
    """
    get account of the company member (employee)
    :return:
    """
    if fund_id is None:
        raise ValueError('event_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising).where(Fundraising.id == fund_id)
    result = session.execute(query).scalars().first()
    return result


def _get_all_fundraisings(account_id: int, session: Session) -> [Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising).where(Fundraising.account_id == account_id)
    result = session.execute(query).scalars().all()
    return result


def _get_all_open_fundraising(account_id: int, session: Session) -> [Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising)\
        .where(Fundraising.account_id == account_id)\
        .where(date.today() + timedelta(days=7) <= Fundraising.event_date)  # через 7 дней после даты события

    result = session.execute(query).scalars().all()
    return result


def _get_all_closed_fundraising(account_id: int, session: Session) -> [Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising)\
        .where(Fundraising.account_id == account_id)\
        .where(date.today() + timedelta(days=7) > Fundraising.event_date)  # через 7 дней после даты события

    result = session.execute(query).scalars().all()
    return result


def _insert_fundraising(account_id: int, session: Session, **kvargs) -> Fundraising:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")
    kvargs['account_id'] = account_id

    event = Fundraising()
    for field in Fundraising.get_fields():
        if field in kvargs:
            setattr(event, field, kvargs[field])
    session.add(event)
    session.commit()

    # включить создателя сбора в список доноров
    account = _get_account(account_id, session)
    if account.user_id is not None:
        _insert_donor(event.id, account.user_id, session)
    if account.company_id is not None:
        user_id = account.company.admin.id
        _insert_donor(event.id, user_id, session)
    return event


def _update_fundraising(fund_id: int, session: Session, **kvargs) -> Fundraising | None:
    if fund_id is None:
        raise ValueError('event_id can not be None')
    if session is None:
        raise ValueError("session can't be None")
    kvargs.pop('fund_id', None)
    kvargs.pop('account_id', None)

    event = _get_fundraising(fund_id, session)
    if event is None:
        return None

    for field in Fundraising.get_fields():
        if field in kvargs:
            setattr(event, field, kvargs[field])
    session.commit()
    return event


# **********************************************************************
# Donor
# **********************************************************************
def _get_donor(fund_id: int, user_id: int, session: Session) -> Donor | None:
    if fund_id is None:
        raise ValueError('event_id can not be None')
    if user_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor: Donor = session.get(Donor, (fund_id, user_id))
    return donor


def _insert_donor(fund_id: int, user_id: int, session: Session) -> Donor | None:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = _get_donor(fund_id, user_id, session)
    if donor is not None:
        return donor

    donor = Donor(fund_id=fund_id, user_id=user_id)
    session.add(donor)
    session.commit()
    return donor


def _update_donor(fund_id: int, user_id: int, session: Session, pay_sum: int) -> Donor:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = _get_donor(fund_id, user_id, session)
    if donor is None:
        donor = _insert_donor(fund_id, user_id, session)

    donor.payed = pay_sum
    session.commit()
    return donor


def _delete_donor(fund_id: int, user_id: int, session: Session) -> bool:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = _get_donor(fund_id, user_id, session)
    if donor:
        session.delete(donor)
        session.commit()
        return True
    return False


def _get_donors(fund_id, session: Session) -> [Donor]:
    if fund_id is None:
        raise ValueError('fund_id can not be None')

    query = select(Donor).where(Donor.fund_id == fund_id)
    result = session.execute(query).scalars().all()
    return result


def _is_fundraising_open(fund_id: int, session: Session) -> bool | None:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    fund = _get_fundraising(fund_id, session)
    if fund is None:
        return None
    days_left = get_days_left(fund.event_date)
    is_open = True if days_left > -7 else False
    return is_open


def _get_fund_avg_sum(fund_id: int, session: Session) -> float:
    """
    Average check of a donor in a fundraising
    """
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    total_sum = _get_fund_total_sum(fund_id, session)
    if total_sum == 0:
        return 0.0

    donor_count = _get_payed_donor_count(fund_id, session)
    if donor_count == 0:
        return 0.0
    avg_sum = round(total_sum / donor_count, 2)
    return avg_sum


def _get_fund_total_sum(fund_id: int, session: Session) -> int:
    """
    Sum of all money raised by fundraising donors
    """
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    total_sum = session.scalar(
        select(func.sum(Donor.payed)).select_from(Donor).where(Donor.fund_id == fund_id)
    )
    if total_sum is None:
        total_sum = 0
    return total_sum


def _get_all_donor_count(fund_id: int, session: Session) -> int:
    """
    Get number of fundraising donors
    """
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    count = session.scalar(
        select(func.count()).select_from(Donor).where(Donor.fund_id == fund_id)
    )
    if count is None:
        count = 0
    return count


def _get_donors_count_by_user(user_id: int, session: Session) -> int:
    """
    Get number of donor fundraising by user
    """
    if user_id is None:
        raise ValueError('fund_id can not be None')
    count = session.scalar(
        select(func.count()).select_from(Donor).where(Donor.user_id == user_id)
    )
    if count is None:
        count = 0
    return count


def _get_payed_donor_count(fund_id, session) -> int:
    """
    Get number of fundraising donors
    """
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    count = session.scalar(
        select(func.count()).select_from(Donor).where(Donor.fund_id == fund_id).where(Donor.payed > 0)
    )
    if count is None:
        count = 0
    return count


def init_texts_tbl(session: Session = None):
    data = [
        ('welcome_invited', 'Приветствую вас! \n Я создан для сбора на подарки для вас и ваших коллег из компании {}. '
                            'Для завершения регистрации, пожалуйста, заполните анкету, '
                            'чтобы коллеги могли поздравить вас.'),
        ('open_events', 'Открытые сборы: {open_events_len}'),
        ('closed_events', 'Закрытые сборы: {closed_events_len}'),
        ('shareEvent', 'Здравствуйте! У {} скоро день рождения.\\nЭто ссылка для сбор на подарок. Присоединяйтесь!'),
        ('user_menu', 'Здравствуйте, {name}!\nЗдесь вы можете оценить свою активность\n\nУчастие в сборах:'
                      ' {donors_len}\nСоздано сборов: {funds_len}\n'
                      'Ваши компании: {companies_len}\nОткрытые сборы: {open_funds_len}'),
        ('trial_menu', 'Здравствуйте, {name}!\nЗдесь вы можете управлять бесплатным сбором'),
        ('company_invite', 'Зарегистрируйтесь, чтобы участвовать в сборах и получать поздравления от друзей.'),
        ('event_accepted', 'Тип события: {type}\nКому: {target}\nК вашему сбору присоединился пользователь. <{name}>.'),
        ('user_congratulation', 'Здравствуйте, {name}!\n\nУра, через 2 недели у вас день рождения :)\n\n'
                                'Отправьте эту ссылку человеку, которому вы доверяете общение со мной.\n\n'
                                'Пожалуйста, не затягивайте.'),
        ('admin_congratulation', 'Здравствуйте, {admin_name}!\n\nУ ваших друзей скоро дни рождения.{user_name} '
                                 'отмечает свой праздник {dob}.\n\nК сожалению, я не могу организовать сбор '
                                 'на подарки, так как у вас нет оплаченных событий.\n\nПожалуйста, '
                                 'оплатите сбор сейчас, чтобы я помог вам поздравить друга.'),
        ('payment', 'Сейчас у вас подключен тариф:\n\nДоступные сборы:'),
        ('welcome', 'Вы можете зарегистрироваться только для одного сбора или сразу зарегистрировать вашу компанию, '
                    'если планируете и дальше использовать Дружбу.'),
        ('event_invite', 'Здравствуйте! Я - Дружба.\nПомогаю организовать сбор денег для любого праздника.\n'
                         'Вы быстро соберёте нужную сумму, чтобы купить подарок коллеге или поздравить друга '
                         'с днём рождения.\\nВам не придётся напоминать о сборе каждому участнику и вручную '
                         'вести учёт собранных денег. Я всё возьму на себя.\nНачнём дружить?'),
        ('event_invite_2', 'Вас пригласил {event_owner}, чтобы подготовить подарок: {event_type} {event_target} '
                           '{campaing_start}. \nПожалуйста, заполните анкету для регистрации.\nТак вы сможете '
                           'участвовать в других сборах, а я напомню друзьям, когда у вас день рождения.'),
        ('event_invite_1', 'Здравствуйте. \nДобро пожаловать в Дружбу, я бот-помощник для сбора на подарки.\n'
                           'Вас пригласил {event_owner}, чтобы подготовить подарок: {event_type} {event_target} '
                           '{campaing_start}.'),
        ('event_deposit', 'Пожалуйста, введите сумму, которую вы перевели для того, чтобы я ее учла.'),
        ('event_deposit_finish', 'Спасибо, вы отличный друг!'),
        ('event_accept', 'Другие участники уже сдали на подарок в среднем по {average_price}. Присоединяйтесь.\n'
                         'Отправить деньги на подарок можно сюда: {event_recieve_link}'),
        ('company_menu', 'Здравствуйте, {name}!\nЗдесь вы можете посмотреть статистику компании {cname}\n\n{link}\n'
                         'Доступны оплаченные сборы: {payed_events}\nСоздано сборов: {created_events_len}\n'
                         'Успешные сборы: {succeded_events}\nУчастники компании: {employees_len}\n'
                         'Из них участвовали в сборах: {participants_len}\n'
                         'Количество переводов в сборах: {event_transfers}\n'
                         'Сумма всех сборов: {events_sum}\n'
                         'Средний чек: {avg_price}\nОткрытые сборы: {open_events}'),
        ('event_declined', 'Тип события: {type}\nКому: {target}\n'
                           'К вашему сбору отказался присоединится пользователь. <{name}>.'),
        ('event_deposited', 'Тип события: {type}\\nКому: {target}\n\n<{name}> перевел <{deposit} руб>'),
        ('admin_notpayeddob', '\n	Здравствуйте, {admin_name}!\n\nУ ваших друзей скоро дни рождения.{user_name} '
                              'отмечает свой праздник {dob}.\n\nК сожалению, я не могу организовать сбор на подарки, '
                              'так как у вас нет оплаченных событий.\n\nПожалуйста, оплатите сбор сейчас, '
                              'чтобы я помог вам поздравить друга.'),
        ('start_message', 'Я рада, что вы выбрали меня  для помощи со сбором.\n\nВы можете зарегистрироваться только '
                          'для одного сбора или сразу зарегистрировать вашу компанию, если планируете и дальше '
                          'использовать Дружбу. Попробуйте первый сбор бесплатно!'),
    ]
    if session is None:
        session = get_session()
    for name, value in data:
        _insert_msg(name, value, session)


# **********************************************************************
# Payment
# **********************************************************************
def _get_payment(payment_id: int, session: Session) -> Payment | None:
    if payment_id is None:
        raise ValueError('payment_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    payment: Payment = session.get(Payment, payment_id)
    return payment


def _insert_payment(account_id: int, session: Session, **kvargs) -> Payment:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")
    kvargs['account_id'] = account_id

    payment = Payment()
    for field in Payment.get_fields():
        if field in kvargs:
            setattr(payment, field, kvargs[field])
    session.add(payment)
    session.commit()
    return payment


def _delete_payment(payment_id: int, session: Session) -> bool:
    if payment_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    payment = _get_payment(payment_id, session)
    if payment:
        session.delete(payment)
        session.commit()
        return True
    return False


def _delete_user_payments(user_id: int, session: Session) -> int:
    """
    Удалить платежи аккаунта пользователя
    :param user_id:
    :param session:
    :return:
    """
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    deleted_payment_count = 0
    account = _get_user_account(user_id, session)
    if account is not None:
        query = select(Payment).where(Payment.account_id == account.id)
        account_payments = session.execute(query).scalars().all()
        for payment in account_payments:
            session.delete(payment)
            deleted_payment_count += 1
        session.commit()

    return deleted_payment_count


def _delete_user_donors(user_id: int, session: Session) -> int:
    """
    Удалить платежи аккаунта пользователя
    :param user_id:
    :param session:
    :return:
    """
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    deleted_count = 0
    query = select(Donor).where(Donor.user_id == user_id)
    user_donors = session.execute(query).scalars().all()
    for donor in user_donors:
        session.delete(donor)
        deleted_count += 1

    return deleted_count


def _get_payments_count(account_id: int, session: Session) -> int:
    """
    Количество платежей с аккаунта
    """
    if account_id is None:
        raise ValueError('account can not be None')
    count = session.scalar(
        select(func.count()).select_from(Payment).where(Payment.account_id == account_id)
    )
    if count is None:
        count = 0
    return count


# **********************************************************************
# Call from backend
# **********************************************************************
class UserStatus(Enum):
    """
    Статус пользователя
    """
    Visitor = 0         # новый посетитель
    TrialUser = 1       # пользователь без оплаты
    User = 2            # пользователь
    Admin = 3           # админ компании, управляет аккаунтом компании
    Donor = 5           # зарегистрированный донор (спонсор)
    AnonymousDonor = 6  # анонимный донор (спонсор)
    Unknown = 12        # фиг его знает, кто это такой


def get_user_id_by_account(account_id) -> int | None:
    """
    вернуть id владельца аккаунта
    """
    session = get_session()
    account: Account = _get_account(account_id, session)
    if account is not None:
        if account.user_id is not None:
            return account.user_id
        company = _get_company(account.company_id, session)
        if company is not None:
            return company.admin_id
    return None


def get_account(account_id) -> ApiAccount:
    session = get_session()
    account: Account = _get_account(account_id, session)
    api_account = ApiAccount(id=account.id, user_id=account.user_id,
                             company_id=account.company_id, payed_evens=account.payed_events)
    return api_account


def create_user(user: ApiUser) -> (User, Account):
    session = get_session()
    session.expire_on_commit = False
    user_id = user.id
    user_data: dict = user.dict()
    user_data.pop('id')
    user = _register_user(user_id, session, **user_data)
    return user, user.account


def get_user(user_id: int) -> User | None:
    session = get_session()
    user: User = _get_user(user_id, session)
    api_user: ApiUser = None
    if user is not None:
        api_user = ApiUser(id=user.id, name=user.name, timezone=user.timezone, birthdate=user.birthdate)
    return api_user


def get_api_user_account(user_id: int) -> ApiAccount | None:
    session = get_session()
    account: Account = _get_user_account(user_id, session)
    api_account = None
    if account is not None:
        api_account = ApiAccount(id=account.id, user_id=account.user_id, company_id=account.company_id,
                                 payed_events=account.payed_events)
    return api_account


def remove_user(user_id: int):
    """
    Удалить из БД пользователя
    """
    session = get_session()
    user: User = _get_user(user_id, session)
    if user is None:
        return

    account: Account = user.account
    if account is None:
        return

    for payment in account.payments:    # удалить платежи
        session.delete(payment)

    for fund in account.fundraisings:   # удалить сборы
        fund_donors = fund.donors
        for fd in fund_donors:          # удалить доноров сбора
            session.delete(fd)
        session.delete(fund)

    for donor in user.donors:           # удалить донорство в других сборах
        session.delete(donor)

    for member in user.members:         # удалить участие в компаниях
        session.delete(member)

    session.delete(account)
    session.delete(user)
    session.commit()


def remove_user_payments(user_id: int):
    """
    Удалить из БД платежи пользователя
    :param user_id:
    :return:
    """
    session = get_session()
    user: User = _get_user(user_id, session)
    account: Account = user.account

    account.payed_events = 0
    for payment in account.payments:    # удалить платежи
        session.delete(payment)
    session.commit()


def create_fundraising(account_id: int, fund: ApiFundraising) -> ApiFundraising | None:
    """
    Создать сбор
    :param account_id: аккаунт пользователя
    :param fund: данные о создаваемом сборе
    :return:
    """
    session = get_session()

    fund_data = fund.dict()
    fund_data.pop('account_id', None)
    fund: Fundraising = _insert_fundraising(account_id, session, **fund_data)

    if fund.owner.payed_events > 0:
        fund = asyncio.run(start_fund(fund.id))

    fund: ApiFundraising = ApiFundraising(id=fund.id, reason=fund.reason, target=fund.target,
                                          account_id=fund.account_id, start=fund.start, end=fund.end,
                                          event_date=fund.event_date, transfer_info=fund.transfer_info,
                                          gift_info=fund.gift_info, congratulation_date=fund.congratulation_date,
                                          congratulation_time=fund.congratulation_time, event_place=fund.event_place,
                                          event_dresscode=fund.event_dresscode, invite_url=fund.invite_url,
                                          chat_url=fund.chat_url)
    return fund


def get_trial_fund_id(user_id) -> int | None:
    """
    Найти id пробного (бесплатного) сбора
    """
    session = get_session()
    account = _get_user_account(user_id, session)
    if account is None:
        return None

    trial_fund_id = session.scalar(
        select(func.min(Fundraising.id)).select_from(Fundraising).where(Fundraising.account_id == account.id)
    )
    return trial_fund_id


def get_fund(fund_id: int) -> ApiFundraising:
    """
    Дать сбор для последующего редактирования
    :param fund_id: уникальный идентификатор сбора
    """
    session = get_session()
    fund = _get_fundraising(fund_id, session)

    api_fund = ApiFundraising.get_empty()
    if fund is not None:
        api_fund.id = fund_id
        api_fund.reason = fund.reason
        api_fund.target = fund.target
        api_fund.account_id = fund.account_id
        api_fund.start = fund.start
        api_fund.end = fund.end
        api_fund.event_date = fund.event_date
        api_fund.transfer_info = fund.transfer_info
        api_fund.gift_info = fund.gift_info
        api_fund.congratulation_date = fund.congratulation_date
        api_fund.congratulation_time = fund.congratulation_time
        api_fund.event_place = fund.event_place
        api_fund.event_dresscode = fund.event_dresscode
        api_fund.invite_url = fund.invite_url

    return api_fund


def update_fund(fund_id: int, api_fund: ApiFundraising) -> bool:
    """
    Обновить информацию о сборе
    :param fund_id: уникальный код сбора
    :param api_fund: данные для корректировки
    """
    session = get_session()
    kvargs: dict = api_fund.dict()
    # Эти поля пользователь не должен изменять, FK не даст изменить _update_fundraising
    kvargs.pop('start', None)
    kvargs.pop('stop', None)
    kvargs.pop('invite_url', None)
    kvargs.pop('chat_url', None)
    fund = _update_fundraising(fund_id, session, **kvargs)
    return fund is not None


def get_fund_info(fund_id: int) -> FundraisingInfo:
    """
    Вернуть статистику по
    :param fund_id:
    :return:
    """
    session = get_session()
    fund = _get_fundraising(fund_id, session)

    fund_info = FundraisingInfo()
    if fund is not None:
        fund_info.is_open = _is_fundraising_open(fund_id, session)
        fund_info.reason = fund.reason
        fund_info.target = fund.target
        fund_info.event_date = fund.event_date.strftime("%m.%d.%Y")
        fund_info.days_left = get_days_left(fund.event_date)
        fund_info.donor_count = _get_all_donor_count(fund_id, session)
        fund_info.payed_count = _get_payed_donor_count(fund_id, session)
        fund_info.total_sum = _get_fund_total_sum(fund_id, session)
        fund_info.avg_sum = _get_fund_avg_sum(fund_id, session)
        fund_info.is_ok = fund_info.total_sum > 0
        fund_info.invite_url = fund.invite_url

    return fund_info


def get_user_info(user_id: int) -> ApiUserInfo:
    session = get_session()
    account = _get_user_account(user_id, session)
    funds = _get_all_fundraisings(account.id, session)
    open_fundraisings = _get_all_open_fundraising(account.id, session)
    companies = _get_user_companies(user_id, session)
    admins = [company for company in companies if company.admin_id == user_id]

    donors_count = _get_donors_count_by_user(user_id, session)
    funds_count = len(funds) if funds is not None else 0
    open_funds = len(open_fundraisings) if open_fundraisings is not None else 0
    company_count = len(companies) if companies is not None else 0
    admin_count = len(admins) if account is not None else 0

    user_info = ApiUserInfo(donors_count=donors_count, funds_count=funds_count, open_funds=open_funds,
                            company_count=company_count, admin_count=admin_count)
    return user_info


def get_user_status(user_id: int, account_id: int = None, has_invite_url: bool = False) -> UserStatus:
    """
    Определить статус пользователя
    :param user_id: телеграм id
    :param account_id: id аккаунта
    :param has_invite_url: признак входа по приглашению
    :return: статус пользователя телеграм (UserStatus)
    """
    session = get_session()
    is_registered: bool = _is_user_registered(user_id, session)

    if not is_registered and has_invite_url:
        return UserStatus.AnonymousDonor
    if is_registered and has_invite_url:
        return UserStatus.Donor

    if not is_registered and not has_invite_url:
        return UserStatus.Visitor

    user_account = _get_user_account(user_id, session)
    if user_account is not None:
        payment_count = _get_payments_count(user_account.id, session)
        if payment_count > 0:
            return UserStatus.User
        return UserStatus.TrialUser

    companies = _get_user_companies(user_id, session)

    if account_id is None:
        return UserStatus.Visitor

    account = _get_account(account_id, session)
    assert account is not None

    if account.user_id is not None and account.company_id is None:  # TrialUser or User
        payments_count = _get_payments_count(account_id, session)
        return UserStatus.TrialUser if payments_count == 0 else UserStatus.User

    if account.user_id is None and account.company_id is not None:
        return UserStatus.Admin

    return UserStatus.Unknown


def get_user_name(user_id) -> str:
    session = get_session()
    user = _get_user(user_id, session)
    return user.name if user is not None else ''


def delete_donor(fund_id: int, user_id: int) -> bool:
    session = get_session()
    ok = _delete_donor(fund_id, user_id, session)
    return ok


def set_fund_admin(fund_id: int, user_id: int) -> bool:
    session = get_session()
    new_account = _get_user_account(user_id, session)
    if new_account is None:
        return False
    fund: Fundraising = _get_fundraising(fund_id, session)
    if fund is None:
        return False
    fund.account_id = new_account.id
    session.commit()
    return True


def get_fund_donors(fund_id) -> ApiDonor:
    session = get_session()
    donors = _get_donors(fund_id, session)
    result = []
    for donor in donors:
        api_donor = ApiDonor(fund_id=donor.fund_id, user_id=donor.user_id, payed_date=donor.payed_date,
                             payed=donor.payed, name=donor.user.name)
        result.append(api_donor)
    return result


def is_fund_open(fund_id) -> bool:
    """
    Проверить состояние сбора (открыт или закрыт)
    """
    session = get_session()
    return _is_fundraising_open(fund_id, session)


def get_available_funds(account_id) -> int:
    """
    Вернуть количество доступных сборов
    """
    session = get_session()
    account: Account = _get_account(account_id, session)
    if account is None:
        return 0
    return account.payed_events


def get_not_started_fund_id(account_id: int) -> int | None:
    """
    Выдать id не запущенного сбора с наименьшим id
    (у не запущенного сбора нет ссылки на сбор и пустое поле start)
    :param account_id:
    :return:
    """
    session = get_session()
    query = select(Fundraising)\
        .where(Fundraising.account_id == account_id) \
        .where(Fundraising.start == None) \
        .order_by(Fundraising.id)
    result: Fundraising = session.execute(query).scalars().first()
    return result.id if result is not None else None


async def start_fund(fund_id: int) -> Fundraising:
    session = get_session()
    fund = _get_fundraising(fund_id, session)
    fund.start = date.today()

    bot_url = await get_bot_url()
    invite_url = f'{bot_url}?start=fund_{fund_id}'
    fund.invite_url = invite_url

    chat_name = f'{fund.reason} {fund.event_date.strftime("%d.%m.%Y")}'
    # chat_url = run(async_create_chat2, chat_name)
    # fund.chat_url = chat_url
    fund.chat_url = 'временно не доступен'
    fund.owner.payed_events -= 1
    session.commit()
    return fund


def get_message_text(text_name: str) -> str:
    session = get_session()
    txt = get_msg(text_name, session).text_value.replace("\\n", "\n")
    return txt


def add_account_payment(result: ApiPaymentResult):
    account_id = result.account_id
    session = get_session()
    account = _get_account(account_id, session)
    # update account
    payed_events = account.payed_events + result.payed_events
    _update_account(account_id, session, payed_events=payed_events)
    # insert payment
    data = {
        'payment_date': date.today(),
        'payed_events': result.payed_events,
        'payment_sum': result.payed_sum,
        'transaction_id': result.transaction_id
    }
    _insert_payment(account_id, session, **data)


def about_fund_info(fund_id) -> str:
    """
    Сформировать экран приветствия донора, анонимного донора
    :param fund_id:
    :return:
    """
    session = get_session()
    fund: Fundraising = _get_fundraising(fund_id, session)
    account = _get_account(fund.account_id, session)
    user_name = account.user.name

    msg = f'Вас пригласил {user_name}, чтобы подготовить подарок.\n\n'
    msg += f'Тип события: {fund.reason}\n' if fund.reason else ''
    msg += f'Кому собираем: {fund.target}\n' if fund.target else ''
    msg += f'Дата события: {fund.event_date}\n' if fund.event_date else ''
    msg += f'Варианты подарков: {fund.gift_info}\n' if fund.gift_info else ''
    msg += f'Дата поздравления: {fund.congratulation_date}\n' if fund.congratulation_date else ''
    msg += f'Время: {fund.congratulation_time}\n' if fund.congratulation_time else ''
    msg += f'Где поздравляем: {fund.event_place}\n' if fund.event_place else ''
    msg += f'Дресс-код: {fund.event_dresscode}\n' if fund.event_dresscode else ''
    return msg


def transfer_fund_info(fund_id) -> str:
    session = get_session()
    fund: Fundraising = _get_fundraising(fund_id, session)
    avg_sum = _get_fund_avg_sum(fund_id, session)

    msg = f'Другие участники уже сдали на подарок в среднем по {avg_sum} руб>. Присоединяйтесь.\n\n'
    msg += f'Отправить деньги на подарок можно сюда:\n{fund.transfer_info}\n\n'
    msg += f'Поучаствовать в обсуждении можно в этом чате, созданном специально для этого сбора:\n\n{fund.chat_url}'
    return msg


def save_money_transfer(fund_id: int, user_id: int, user_name: str, sum_money: int) -> bool:
    """
    Записать перевод донора
    :param fund_id: сбор
    :param user_id: донор
    :param user_name: имя анонимного донора
    :param sum_money: сумма перевода
    :return:
    """
    session = get_session()
    fund: Fundraising = _get_fundraising(fund_id, session)
    donors = [d for d in fund.donors if d.user_id == user_id]
    if len(donors) == 0:
        user = _insert_user(user_id, session, name=user_name)
        donor: Donor = _insert_donor(fund_id, user_id, session)
    else:
        donor: Donor = donors[0]
    donor.payed += sum_money
    donor.payed_date = date.today()
    session.commit()
    return True
