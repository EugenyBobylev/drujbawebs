from datetime import date, timedelta

from sqlalchemy import create_engine, Engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from config import Config
from db.models import Msg, User, Company, Account, Fundraising, Donor, Payment, MC
from utils import get_days_left


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


def db_get_msg(text_name: str, session: Session) -> Msg | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(Msg).where(Msg.text_name == text_name)
    result = session.execute(query).scalars().first()
    return result


def db_insert_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = db_get_msg(text_name, session)
    if msg:
        msg = db_update_msg(text_name, text_value, session)
    else:
        msg = Msg(text_name=text_name, text_value=text_value)
        session.add(msg)
        session.commit()
    return msg


def db_update_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = db_get_msg(text_name, session)
    if msg:
        msg.text_value = text_value
        session.commit()
    else:
        msg = db_insert_msg(text_name, text_value, session)
    return msg


def db_delete_msg(text_name: str, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    msg = db_get_msg(text_name, session)
    if msg:
        session.delete(msg)
        session.commit()


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
        ('start_message', 'Я рада, что вы выбрали меня для помощи со сбором.\n\nВы можете зарегистрироваться только '
                          'для одного сбора или сразу зарегистрировать вашу компанию, если планируете и дальше '
                          'использовать Дружбу.\nПопробуйте первый сбор бесплатно!'),
    ]
    if session is None:
        session = get_session()
    for name, value in data:
        db_insert_msg(name, value, session)


# **********************************************************************
#  User
# **********************************************************************
def db_get_user(user_id: int, session: Session) -> User | None:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    return user


def db_insert_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user is not None:
        return user

    user = User(id=user_id)
    for field in User.get_fields():
        if field in kvargs:
            setattr(user, field, kvargs[field])
    session.add(user)
    session.commit()
    return user


def db_update_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user is None:
        user = db_insert_user(user_id, session, **kvargs)
    else:
        for field in User.get_fields():
            if field in kvargs:
                setattr(user, field, kvargs[field])
        session.commit()
    return user


def db_delete_user(user_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()


def db_register_user(user_id: int, session: Session, **kvargs) -> User:
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    user = session.get(User, user_id)
    if user:
        user = db_update_user(user_id, session, **kvargs)
        account = db_get_user_account(user_id, session)
        if account is None:
            db_insert_user_account(user.id, session)
        session.refresh(user)
        return user

    user = db_insert_user(user_id, session, **kvargs)
    account = db_insert_user_account(user.id, session)
    assert account is not None
    return user


def db_is_user_registered(user_id: int, session: Session) -> bool:
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    user = session.get(User, user_id)
    if user is not None:
        return len(user.accounts) > 0
    return False


def db_get_user_companies(user_id: int, session: Session) -> [Company]:
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
def db_get_account(account_id: int, session: Session = None) -> Account | None:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.get(Account, account_id)
    return account


def db_get_user_account(user_id: int, session: Session = None) -> Account | None:
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(Account).where(Account.user_id == user_id)
                              .where(Account.company_id == None)).first()
    return account


def db_get_user_all_accounts(user_id: int, session: Session = None) -> list[Account]:
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    accounts = session.scalars(select(Account).where(Account.user_id == user_id)).all()
    return accounts


def db_get_company_account(company_id: int, session: Session = None) -> Account | None:
    if company_id is None:
        raise ValueError('company_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = session.scalars(select(Account).where(Account.company_id == company_id)
                              .where(Account.user_id == None)).first()
    return account


def db_insert_user_account(user_id: int, session: Session) -> Account:
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


def db_insert_company_account(company_id: int, session: Session) -> Account:
    if company_id is None:
        raise ValueError('company_id can not be None')
    if session is None:
        raise ValueError('session can not be None')
    account = db_get_company_account(company_id, session)
    if account is not None:
        return account

    account = Account(company_id=company_id, payed_events=0)
    session.add(account)
    session.commit()
    return account


def db_update_account(account_id: int, session: Session, **kvargs) -> Account:
    if session is None:
        session = get_session()
    account = db_get_account(account_id, session)
    kvargs.pop('user_id', None)
    kvargs.pop('company_id', None)

    for field in Account.get_fields():
        if field in kvargs:
            setattr(account, field, kvargs[field])
    session.commit()
    return account


def db_delete_account(account_id: int, session: Session):
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
def db_get_company(company_id: int, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    company = session.get(Company, company_id)
    return company


def db_get_company_by_name(name: str, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    company = session.scalars(select(Company).where(Company.name == name)).first()
    return company


def db_insert_company(name: str, admin_id: int, session: Session, **kvargs) -> Company:
    if name is None:
        raise ValueError("name can't be None")
    if admin_id is None:
        raise ValueError("admin_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    company = db_get_company_by_name(name, session)
    if company:
        company.admin_id = admin_id
        db_update_company(company.id, session, **kvargs)
        return company

    company = Company(name=name, admin_id=admin_id)
    for field in Company.get_fields():
        if field in kvargs:
            setattr(company, field, kvargs[field])
    session.add(company)
    session.commit()

    # сразу создать account
    db_insert_company_account(company.id, session)
    session.commit()
    return company


def db_update_company(company_id: int, session: Session, **kvargs) -> Company:
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


def db_delete_company(company_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    company = session.get(Company, company_id)
    if company:
        session.delete(company)
        session.commit()


def db_get_company_users(company_id: int, session: Session) -> [User]:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    company_users = []
    company = session.get(Company, company_id)
    if company is not None:
        company_users = [mc.user for mc in company.members]
    return company_users


def db_get_member_account(company_id: int, user_id: int, session: Session) -> Account | None:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    query = select(Account).where(Account.company_id == company_id).where(Account.user_id == user_id)
    result = session.execute(query).scalars().first()
    return result


def db_add_member(company_id: int, user_id: int, session: Session) -> Account:
    """
    create companies' user account
    """
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    account = db_get_member_account(company_id, user_id, session)
    if account is not None:
        db_update_account(account.id, session, payed_events=0)
        return account

    account = Account(company_id=company_id, user_id=user_id, payed_events=0)
    session.add(account)
    session.commit()
    return account


# **********************************************************************
# MC
# **********************************************************************
def db_get_company_user(user_id: int, company_id: int, session: Session, **kvargs) -> MC | None:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")

    mc = session.get(MC, {'user_id': user_id, 'company_id': company_id})
    return mc


def db_insert_company_user(user_id: int, company_id: int, session: Session, **kvargs) -> MC:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    mc = db_get_company_user(user_id, company_id, session)
    if mc is not None:
        return mc

    mc = MC(user_id=user_id, company_id=company_id)
    for field in MC.get_fields():
        if field in kvargs:
            setattr(mc, field, kvargs[field])
    session.add(mc)
    session.commit()
    return mc


def db_update_company_user(user_id: int, company_id: int, session: Session, **kvargs) -> MC | None:
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    mc = db_get_company_user(user_id, company_id, session)
    if mc is None:
        return None

    for field in MC.get_fields():
        if field in kvargs:
            setattr(mc, field, kvargs[field])
    session.commit()
    return mc


def db_delete_company_user(user_id: int, company_id: int, session: Session):
    if company_id is None:
        raise ValueError("company_id can't be None")
    if user_id is None:
        raise ValueError("user_id can't be None")
    if session is None:
        raise ValueError("session can't be None")
    mc = session.get(MC, {'user_id': user_id, 'company_id': company_id})
    if mc is not None:
        session.delete(mc)
        session.commit()


# **********************************************************************
# Fundraising
# **********************************************************************
def db_get_fundraising(fund_id: int, session: Session) -> Fundraising | None:
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


def db_get_all_fundraisings(account_id: int, session: Session) -> list[Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising).where(Fundraising.account_id == account_id)
    result = session.execute(query).scalars().all()
    return result


def db_get_all_open_fundraising(account_id: int, session: Session) -> [Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising) \
        .where(Fundraising.account_id == account_id) \
        .where(date.today() + timedelta(days=7) <= Fundraising.event_date)  # через 7 дней после даты события

    result = session.execute(query).scalars().all()
    return result


def db_get_all_closed_fundraising(account_id: int, session: Session) -> [Fundraising]:
    if account_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    query = select(Fundraising) \
        .where(Fundraising.account_id == account_id) \
        .where(date.today() + timedelta(days=7) > Fundraising.event_date)  # через 7 дней после даты события

    result = session.execute(query).scalars().all()
    return result


def db_insert_fundraising(account_id: int, session: Session, **kvargs) -> Fundraising:
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
    account = db_get_account(account_id, session)
    if account.user_id is not None:
        db_insert_donor(event.id, account.user_id, session)
    if account.company_id is not None:
        user_id = account.company.admin.id
        db_insert_donor(event.id, user_id, session)
    return event


def db_update_fundraising(fund_id: int, session: Session, **kvargs) -> Fundraising | None:
    if fund_id is None:
        raise ValueError('event_id can not be None')
    if session is None:
        raise ValueError("session can't be None")
    kvargs.pop('fund_id', None)
    kvargs.pop('account_id', None)

    event = db_get_fundraising(fund_id, session)
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
def db_get_donor(fund_id: int, user_id: int, session: Session) -> Donor | None:
    if fund_id is None:
        raise ValueError('event_id can not be None')
    if user_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = session.get(Donor, (fund_id, user_id))
    return donor


def db_insert_donor(fund_id: int, user_id: int, session: Session) -> Donor | None:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = db_get_donor(fund_id, user_id, session)
    if donor is not None:
        return donor

    donor = Donor(fund_id=fund_id, user_id=user_id)
    session.add(donor)
    session.commit()
    return donor


def db_update_donor(fund_id: int, user_id: int, session: Session, pay_sum: int) -> Donor:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = db_get_donor(fund_id, user_id, session)
    if donor is None:
        donor = db_insert_donor(fund_id, user_id, session)

    donor.payed = pay_sum
    session.commit()
    return donor


def db_delete_donor(fund_id: int, user_id: int, session: Session) -> bool:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    if user_id is None:
        raise ValueError('user_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    donor = db_get_donor(fund_id, user_id, session)
    if donor:
        session.delete(donor)
        session.commit()
        return True
    return False


def db_get_donors(fund_id, session: Session) -> [Donor]:
    if fund_id is None:
        raise ValueError('fund_id can not be None')

    query = select(Donor).where(Donor.fund_id == fund_id)
    result = session.execute(query).scalars().all()
    return result


def db_is_fundraising_open(fund_id: int, session: Session) -> bool | None:
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    fund = db_get_fundraising(fund_id, session)
    if fund is None:
        return None
    days_left = get_days_left(fund.event_date)
    is_open = True if days_left > -7 else False
    return is_open


def db_get_fund_avg_sum(fund_id: int, session: Session) -> float:
    """
    Average check of a donor in a fundraising
    """
    if fund_id is None:
        raise ValueError('fund_id can not be None')
    total_sum = db_get_fund_total_sum(fund_id, session)
    if total_sum == 0:
        return 0.0

    donor_count = db_get_payed_donor_count(fund_id, session)
    if donor_count == 0:
        return 0.0
    avg_sum = total_sum // donor_count
    return avg_sum


def db_get_fund_total_sum(fund_id: int, session: Session) -> int:
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


def db_get_all_donor_count(fund_id: int, session: Session) -> int:
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


def db_get_donors_count_by_user(user_id: int, session: Session) -> int:
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


def db_get_payed_donor_count(fund_id, session) -> int:
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


# **********************************************************************
# Payment
# **********************************************************************
def db_get_payment(payment_id: int, session: Session) -> Payment | None:
    if payment_id is None:
        raise ValueError('payment_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    payment: Payment = session.get(Payment, payment_id)
    return payment


def db_insert_payment(account_id: int, session: Session, **kvargs) -> Payment:
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


def db_delete_payment(payment_id: int, session: Session) -> bool:
    if payment_id is None:
        raise ValueError('account_id can not be None')
    if session is None:
        raise ValueError("session can't be None")

    payment = db_get_payment(payment_id, session)
    if payment:
        session.delete(payment)
        session.commit()
        return True
    return False


def db_delete_user_payments(user_id: int, session: Session) -> int:
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
    account = db_get_user_account(user_id, session)
    if account is not None:
        query = select(Payment).where(Payment.account_id == account.id)
        account_payments = session.execute(query).scalars().all()
        for payment in account_payments:
            session.delete(payment)
            deleted_payment_count += 1
        session.commit()

    return deleted_payment_count


def db_delete_user_donors(user_id: int, session: Session) -> int:
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


def db_get_payments_count(account_id: int, session: Session) -> int:
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


def db_get_last_payment(account_id, session) -> Payment | None:
    """
    Количество платежей с аккаунта
    """
    if account_id is None:
        raise ValueError('account can not be None')

    query = session.query(Payment, account_id).where(Payment.account_id == account_id).order_by(Payment.id.desc())
    payment: Payment = session.execute(query).scalars().first()
    return payment
