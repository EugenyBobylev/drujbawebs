from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import sessionmaker, Session

from config import BotConfig
from db.models import Msg, User, Company


def get_engine() -> Engine:
    config = BotConfig.instance()
    url = config.get_postgres_url()
    engine = create_engine(url, pool_size=50, echo=False)
    return engine


def get_session(eng: Engine = None) -> Session:
    if eng is None:
        eng = get_engine()
    _Session = sessionmaker(bind=eng)
    session = _Session()
    return session


def get_msg(text_name: str, session: Session) -> Msg | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(Msg).where(Msg.text_name == text_name)
    result = session.execute(query).scalars().first()
    return result


def insert_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        msg = update_msg(text_name, text_value, session)
    else:
        msg = Msg(text_name=text_name, text_value=text_value)
        session.add(msg)
        session.commit()
    return msg


def update_msg(text_name: str, text_value: str, session: Session) -> Msg:
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        msg.text_value = text_value
        session.commit()
    else:
        msg = insert_msg(text_name, text_value, session)
    return msg


def delete_msg(text_name: str, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    msg = get_msg(text_name, session)
    if msg:
        session.delete(msg)
        session.commit()


def get_user(user_id: int, session: Session) -> User | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(User).where(User.id == user_id)
    result = session.execute(query).scalars().first()
    return result


def create_user(user) -> User:
    session = get_session()
    session.expire_on_commit = False
    tgid = user.id
    user_data: dict = user.dict()
    user_data.pop('id')
    user = insert_user(tgid, session, **user_data)
    return user


def insert_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = get_user(user_id, session)
    if user:
        user = update_user(user_id, session, **kvargs)
    else:
        user = User(id=user_id)
        for field in User.get_fields():
            if field in kvargs:
                setattr(user, field, kvargs[field])
        session.add(user)
        session.commit()
    return user


def update_user(user_id: int, session: Session, **kvargs) -> User:
    if session is None:
        raise ValueError("session can't be None")
    user = get_user(user_id, session)
    if user is None:
        user = insert_user(user_id, session, **kvargs)
    else:
        for field in User.get_fields():
            if field in kvargs:
                setattr(user, field, kvargs[field])
        session.commit()
    return user


def delete_user(user_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    user = get_user(user_id, session)
    if user:
        session.delete(user)
        session.commit()


def get_company(company_id: int, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(Company).where(Company.id == company_id)
    result = session.execute(query).scalars().first()
    return result


def get_company_by_name(name: str, session: Session) -> Company | None:
    if session is None:
        raise ValueError("session can't be None")
    query = select(Company).where(Company.name == name)
    result = session.execute(query).scalars().first()
    return result


def insert_company(owner_id: int, session: Session, **kvargs) -> Company:
    if session is None:
        raise ValueError("session can't be None")
    company = Company()
    company.owner_id = owner_id
    for field in Company.get_fields():
        if field in kvargs:
            setattr(company, field, kvargs[field])
    session.add(company)
    session.commit()
    return company


def update_company(company_id: int, session: Session, **kvargs) -> Company:
    if session is None:
        raise ValueError("session can't be None")
    company = get_company(company_id, session)
    if company is None:
        raise ValueError("company_id not found")
    fields = Company.get_fields()
    for field in fields:
        if field in kvargs:
            setattr(company, field, kvargs[field])
    session.commit()
    return company


def delete_company(company_id: int, session: Session):
    if session is None:
        raise ValueError("session can't be None")
    company = get_company(company_id, session)
    if company:
        session.delete(company)
        session.commit()



def init_texts_tbl(session: Session = None):
    data = [
        ('welcome_invited',	'Приветствую вас! \n Я создан для сбора на подарки для вас и ваших коллег из компании {}. '
                            'Для завершения регистрации, пожалуйста, заполните анкету, '
                            'чтобы коллеги могли поздравить вас.'),
        ('open_events',	'Открытые сборы: {open_events_len}'),
        ('closed_events', 'Закрытые сборы: {closed_events_len}'),
        ('shareEvent', 'Здравствуйте! У {} скоро день рождения.\\nЭто ссылка для сбор на подарок. Присоединяйтесь!'),
        ('participant_menu', 'Здравствуйте, {name}!\nЗдесь вы можете оценить свою активность\n\nУчастие в сборах:'
                             ' {participated_events_len}\nСоздано сборов: {created_events_len}\n'
                             'Ваши компании: {companies_len}\nОткрытые сборы: {open_events}'),
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
        ('payment',	'Сейчас у вас подключен тариф:\n\nДоступные сборы:'),
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
        insert_msg(name, value, session)
