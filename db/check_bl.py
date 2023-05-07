import os
from datetime import date, timedelta

from sqlalchemy.orm import Session

from db.bl import get_session, insert_user, insert_company, update_user, get_user, get_event, \
    insert_event, get_events_by_owner, update_event, delete_event, get_msg, init_texts_tbl


def create_user_123():
    session = get_session()
    user = {
        'name': 'Егор Летов',
        'timezone': -1,
        'payed_events': 10
    }
    user = insert_user(user_id=123, session=session, **user)
    print(user)
    return user


def create_user_456():
    session = get_session()
    user = {
        'name': 'Ян Френкедь',
        'timezone': 2,
        'payed_events': 8
    }
    user = insert_user(user_id=456, session=session, **user)
    print(user)
    return user


def create_company_123():
    session = get_session()
    company = {
        'name': 'moovon',
        'branch': 'кузня ильича',
        'payed_events': 10,
    }
    company = insert_company(owner_id=123, session=session, **company)
    print(company)
    return company


def create_event_123(session: Session):
    event_data = {
        'type': 'ДР',
        'target': 'фиг его знает',
        'campaign_start': date.today(),
        'campaign_end' : date.today() + timedelta(days=10)
    }
    event = insert_event(owner_id=123, session=session, **event_data)
    print(event)


def update_event_123(session: Session):
    update_data = {
        'target': 'На подарок другу',
    }
    event = update_event(1, session, **update_data)
    print(event)


def check_event(session):
    # create_event_123(session)
    # events = get_events_by_owner(123, session)
    # print(events)
    delete_event(3, session)
    event = get_event(3, session)
    # update_event_123(session)
    print(event)


def check_msg(session):
    msg = get_msg('start_message', session).text_value
    print(msg)


def main():
    # init_texts_tbl()
    session = get_session()

    # user = update_user(user_id=123, session=session, **user)
    user = get_user(user_id=123, session=session)
    print(user)

    # company = get_company(6, session)
    # company = get_company_by_name('moovon', session)
    # company = insert_company(owner_id=123, session=session, **company)
    # company = update_company(6, session, **company)
    # print(company)
    # print(company.owner)
    print(user.companies)
    # delete_company(6, session)


if __name__ == '__main__':
    os.chdir('..')
    _session = get_session()
    # main()
    # check_event(_session)
    # check_msg(_session)
    init_texts_tbl()
