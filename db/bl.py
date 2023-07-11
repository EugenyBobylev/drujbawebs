import asyncio
import json
from datetime import date
from enum import Enum
from json import JSONDecodeError

from sqlalchemy import select, func

from backend import User as ApiUser
from backend import CompanyUser as ApiCompanyUser
from backend import Fundraising as ApiFundraising
from backend import FundraisingInfo as ApiFundraisingInfo
from backend import FundraisingSmallInfo as ApiFundSmallInfo
from backend import Account as ApiAccount
from backend import Donor as ApiDonor
from backend import UserInfo as ApiUserInfo
from backend import PaymentResult as ApiPaymentResult
from backend import ApiUserStatus as ApiUserStatus
from chat.user_chat import async_create_chat

from db.models import User, Company, Account, Fundraising, Donor, Payment
from db.repository import get_session, db_get_account, db_get_company, db_get_user_account, db_update_user, \
    db_get_all_fundraisings, db_get_all_open_fundraising, db_get_user_companies, db_get_donors_count_by_user, \
    db_is_user_registered, db_get_payments_count, db_get_user, db_insert_company, db_insert_company_user, \
    db_update_company_user, db_add_member, db_get_company_account, db_get_company_by_name, db_get_company_user, \
    db_insert_fundraising, db_get_fundraising, db_update_fundraising, db_is_fundraising_open, db_get_all_donor_count, \
    db_get_payed_donor_count, db_get_fund_total_sum, db_get_fund_avg_sum, db_delete_donor, db_get_donors, \
    db_get_last_payment, db_get_msg, db_update_account, db_insert_payment, db_insert_user, db_insert_donor, \
    db_register_user, db_get_user_all_accounts
from utils import get_days_left, get_bot_url


# **********************************************************************
# Call from backend
# **********************************************************************
class UserStatus(Enum):
    """
    Статус пользователя
    """
    Visitor = 0  # новый посетитель
    TrialUser = 1  # пользователь без оплаты
    User = 2  # пользователь
    Admin = 3  # админ компании, управляет аккаунтом компании
    Donor = 5  # зарегистрированный донор (спонсор)
    AnonymousDonor = 6  # анонимный донор (спонсор)
    DonationCheaf = 7  # отвественный за сбор DonationCheaf
    Unknown = 12  # фиг его знает, кто это такой


def get_user_id_by_account(account_id) -> int | None:
    """
    вернуть id владельца аккаунта
    """
    session = get_session()
    account: Account = db_get_account(account_id, session)
    if account is not None:
        if account.user_id is not None:
            return account.user_id
        company = db_get_company(account.company_id, session)
        if company is not None:
            return company.admin_id
    return None


def get_account(account_id) -> ApiAccount:
    session = get_session()
    account: Account = db_get_account(account_id, session)
    api_account = ApiAccount(id=account.id, user_id=account.user_id,
                             company_id=account.company_id, payed_evens=account.payed_events)
    return api_account


def create_user(user: ApiUser) -> (User, Account):
    session = get_session()
    session.expire_on_commit = False
    user_id = user.id
    user_data: dict = user.dict()
    user_data.pop('id')
    user = db_register_user(user_id, session, **user_data)
    return user, user.accounts


def get_user(user_id: int) -> ApiUser | None:
    session = get_session()
    user: User = db_get_user(user_id, session)
    api_user: ApiUser = None
    if user is not None:
        api_user = ApiUser(id=user.id, name=user.name, timezone=user.timezone, birthdate=str(user.birthdate))
    return api_user


def get_user_name(user_id) -> str:
    session = get_session()
    user = db_get_user(user_id, session)
    return user.name if user is not None else ''


def get_api_user_account(user_id: int) -> ApiAccount | None:
    session = get_session()
    account: Account = db_get_user_account(user_id, session)
    api_account = None
    if account is not None:
        api_account = ApiAccount(id=account.id, user_id=account.user_id, company_id=account.company_id,
                                 payed_events=account.payed_events)
    return api_account


def update_user(user_id: int, api_user: ApiUser) -> bool:
    """
    Обновить информацию о пользователе
    :param user_id: уникальный код пользователя
    :param api_user: данные для корректировки
    """
    session = get_session()
    kvargs: dict = api_user.dict()
    user = db_update_user(user_id, session, **kvargs)
    return user is not None


def remove_user(user_id: int):
    """
    Удалить из БД пользователя
    """
    session = get_session()
    user: User = db_get_user(user_id, session)
    if user is None:
        return
    for account in user.accounts:
        if account.company_id is not None:
            session.delete(account.company)
    session.delete(user)
    session.commit()


def get_user_info(user_id: int) -> ApiUserInfo:
    session = get_session()
    account = db_get_user_account(user_id, session)
    funds = db_get_all_fundraisings(account.id, session)
    open_fundraisings = db_get_all_open_fundraising(account.id, session)
    companies = db_get_user_companies(user_id, session)
    admins = [company for company in companies if company.admin_id == user_id]

    donors_count = db_get_donors_count_by_user(user_id, session)
    funds_count = len(funds) if funds is not None else 0
    open_funds = len(open_fundraisings) if open_fundraisings is not None else 0
    company_count = len(companies) if companies is not None else 0
    admin_count = len(admins) if account is not None else 0

    user_info = ApiUserInfo(donors_count=donors_count, funds_count=funds_count, open_funds=open_funds,
                            company_count=company_count, admin_count=admin_count)
    return user_info


def get_user_statuses(user_id: int, has_invite_url: bool = False) -> list[ApiUserStatus]:
    """
    Определить статус пользователя
    :param user_id: телеграм id
    :param account_id: id аккаунта
    :param has_invite_url: признак входа по приглашению
    :return: статус пользователя телеграм (ApiUserStatus)
    """
    session = get_session()
    all_statuses = []

    user: User = db_get_user(user_id, session)
    if user is None and not has_invite_url:
        api_user = ApiUserStatus(user_id=user_id, status=UserStatus.Visitor.name)
        all_statuses.append(api_user)
        return all_statuses
    if user is None and has_invite_url:
        api_user = ApiUserStatus(user_id=user_id, status=UserStatus.AnonymousDonor.name)
        all_statuses.append(api_user)
        return all_statuses

    if len(user.accounts) == 0:
        api_user = ApiUserStatus(user_id=user_id, status=UserStatus.Visitor.name)
        all_statuses.append(api_user)
        return all_statuses

    if has_invite_url:
        api_user = ApiUserStatus(user_id=user_id, status=UserStatus.Donor.name)
        all_statuses.append(api_user)
        return all_statuses

    for account in user.accounts:
        api_user = None

        if account.company_id is None:  # это персональный аккаунт м.б. TrialUser or User
            payments = account.payments
            payments_count = len(payments) if payments is not None else 0
            if payments_count == 0:
                api_user = ApiUserStatus(user_id=user_id, account_id=account.id, status=UserStatus.TrialUser.name)
            elif payments_count > 0:
                api_user = ApiUserStatus(user_id=user_id, account_id=account.id, status=UserStatus.User.name)
            all_statuses.append(api_user)

        elif account.company_id is not None:  # это aккаунт компании или ответственного за сбор
            company = account.company
            if company.admin_id == user_id:
                api_user = ApiUserStatus(user_id=user_id, account_id=account.id,  status=UserStatus.Admin.name,
                                         company_id=company.id, company_nsme=company.name)
                all_statuses.append(api_user)
            funraisings = account.fundraisings
            fund_count = len(funraisings) if funraisings is not None else 0
            if fund_count > 0:
                api_user = ApiUserStatus(user_id=user_id, account_id=account.id, status=UserStatus.DonationCheaf.name,
                                         company_id=company.id, company_nsme=company.name)
                all_statuses.append(api_user)

    return all_statuses

    # is_registered: bool = db_is_user_registered(user_id, session)
    # if not is_registered and has_invite_url:
    #     return ApiUserStatus.AnonymousDonor
    # if is_registered and has_invite_url:
    #     return ApiUserStatus.Donor
    #
    # if not is_registered and not has_invite_url:
    #     return ApiUserStatus.Visitor
    #
    # user_account = db_get_user_account(user_id, session)
    # if user_account is not None:
    #     payment_count = db_get_payments_count(user_account.id, session)
    #     if payment_count > 0:
    #         return ApiUserStatus.User
    #     return ApiUserStatus.TrialUser
    #
    # companies = db_get_user_companies(user_id, session)
    #
    # if account_id is None:
    #     return ApiUserStatus.Visitor
    #
    # account = db_get_account(account_id, session)
    # assert account is not None
    #
    # if account.user_id is not None and account.company_id is None:  # TrialUser or User
    #     payments_count = db_get_payments_count(account_id, session)
    #     return ApiUserStatus.TrialUser if payments_count == 0 else ApiUserStatus.User
    #
    # if account.user_id is None and account.company_id is not None:
    #     return ApiUserStatus.Admin
    #
    # return ApiUserStatus.Unknown


def remove_user_payments(user_id: int):
    """
    Удалить из БД платежи пользователя
    :param user_id:
    :return:
    """
    session = get_session()
    user: User = db_get_user(user_id, session)
    for account in user.accounts:
        account.payed_events = 0
        for payment in account.payments:  # удалить платежи
            session.delete(payment)
    session.commit()


def check_company_exists(company_name: str) -> bool:
    session = get_session()
    company = db_get_company_by_name(company_name, session)
    return company is not None


def create_company_user(company_user: ApiCompanyUser) -> (Company, Account, User, Account):
    """
     Создать компанию/пользователя/пользователя компании все вместе или что-то по отдельности
     возвращаем company, company_account, user, member_account
    """
    session = get_session()
    session.expire_on_commit = False

    # insert new user if it required otherwise update exists user
    user_data = {
        'name': company_user.user_name,
        'birthdate': company_user.birthdate,
        'timezone': company_user.timezone
    }
    user = db_get_user(company_user.user_id, session)
    if user is None:
        user = db_register_user(company_user.user_id, session, **user_data)
    else:
        user = db_update_user(company_user.user_id, session, **user_data)

    # insert new company
    company_data = {
        'industry': company_user.industry,
        'person_count': company_user.person_count,
    }
    company = db_insert_company(company_user.company_name, company_user.user_id, session, **company_data)

    # insert new member of company or update exists member
    mc = db_get_company_user(company_user.user_id, company_user.user_id, session)
    mc_data = {
        'phone': company_user.phone,
        'email': company_user.email,
        'title': company_user.job,
    }
    if mc is None:
        mc = db_insert_company_user(company_user.user_id, company.id, session, **mc_data)
    else:
        mc = db_update_company_user(company_user.user_id, company.id, session, **mc_data)

    # create account for member of company and get account of company
    member_acount: Account = db_add_member(company.id, user.id, session)
    company_account: Account = db_get_company_account(company.id, session)
    return company, company_account, user, member_acount


async def create_company_url(company_id: int) -> str:
    session = get_session()
    company = db_get_company(company_id, session)
    if company is not None:
        bot_url = await get_bot_url()
        company_url = f'{bot_url}?start=company_{company.id}'
        company.company_url = company_url
        session.commit()
        return company.company_url
    return ''


def get_company(company_id: int) -> Company | None:
    session = get_session()
    company = db_get_company(company_id, session)
    return company


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
    fund: Fundraising = db_insert_fundraising(account_id, session, **fund_data)

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
    account = db_get_user_account(user_id, session)
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
    fund = db_get_fundraising(fund_id, session)

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
    fund = db_update_fundraising(fund_id, session, **kvargs)
    return fund is not None


def get_fund_info(fund_id: int) -> ApiFundraisingInfo:
    """
    Вернуть статистику по
    :param fund_id:
    :return:
    """
    session = get_session()
    fund = db_get_fundraising(fund_id, session)

    fund_info = ApiFundraisingInfo()
    if fund is not None:
        is_open = db_is_fundraising_open(fund_id, session)
        fund_info.is_open = is_open
        fund_info.reason = fund.reason
        fund_info.target = fund.target
        fund_info.event_date = fund.event_date.strftime("%d.%m.%Y")
        fund_info.days_left = get_days_left(fund.event_date) if is_open else 0
        fund_info.donor_count = db_get_all_donor_count(fund_id, session)
        fund_info.payed_count = db_get_payed_donor_count(fund_id, session)
        fund_info.total_sum = db_get_fund_total_sum(fund_id, session)
        fund_info.avg_sum = db_get_fund_avg_sum(fund_id, session)
        fund_info.is_ok = fund_info.total_sum > 0
        fund_info.invite_url = fund.invite_url

    return fund_info


def delete_donor(fund_id: int, user_id: int) -> bool:
    session = get_session()
    ok = db_delete_donor(fund_id, user_id, session)
    return ok


def set_fund_admin(fund_id: int, user_id: int) -> bool:
    session = get_session()
    new_account = db_get_user_account(user_id, session)
    if new_account is None:
        return False
    fund: Fundraising = db_get_fundraising(fund_id, session)
    if fund is None:
        return False
    fund.account_id = new_account.id
    session.commit()
    return True


def get_fund_donors(fund_id) -> ApiDonor:
    session = get_session()
    donors = db_get_donors(fund_id, session)
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
    return db_is_fundraising_open(fund_id, session)


async def start_fund(fund_id: int) -> Fundraising:
    session = get_session()
    fund = db_get_fundraising(fund_id, session)
    fund.start = date.today()

    bot_url = await get_bot_url()
    invite_url = f'{bot_url}?start=fund_{fund_id}'
    fund.invite_url = invite_url

    chat_name = f'{fund.reason} {fund.event_date.strftime("%d.%m.%Y")}'
    chat_url = await async_create_chat(chat_name)
    fund.chat_url = chat_url
    # fund.chat_url = 'временно не доступен'

    fund.owner.payed_events -= 1
    session.commit()
    return fund


def get_available_funds(account_id) -> int:
    """
    Вернуть количество доступных сборов
    """
    session = get_session()
    account: Account = db_get_account(account_id, session)
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
    query = select(Fundraising) \
        .where(Fundraising.account_id == account_id) \
        .where(Fundraising.start == None) \
        .order_by(Fundraising.id)
    result: Fundraising = session.execute(query).scalars().first()
    return result.id if result is not None else None


def get_account_funds_info(account_id) -> list[ApiFundSmallInfo]:
    session = get_session()
    data = []
    funds = db_get_all_fundraisings(account_id, session)
    for fund in funds:
        id = fund.id
        target = fund.target
        event_date = fund.event_date.strftime('%d.%m.%Y')

        days_left = get_days_left(fund.event_date)
        is_open = True if days_left > -7 else False

        total_sum = db_get_fund_total_sum(id, session)
        is_success = True if total_sum > 0 else False

        fund_small_info = ApiFundSmallInfo(id=id, target=target, event_date=event_date, is_open=is_open,
                                           is_success=is_success)
        data.append(fund_small_info)
    return data


def get_current_tariff(account_id) -> str:
    """
    вернуть название тарифа, который был последний оплачен, либо Пробный тариф если оплат еще не было
    :param account_id:
    :return:
    """
    session = get_session()
    payment: Payment = db_get_last_payment(account_id, session)
    if payment is None:
        return 'Пробный'
    cnt = payment.payed_events
    if 1 <= cnt <= 5:
        return 'Знакомый'
    elif 6 <= cnt <= 49:
        return 'Приятель'
    elif 50 <= cnt <= 99:
        return 'Напарник'
    elif cnt >= 100:
        return 'Лучший друг'


def get_message_text(text_name: str) -> str:
    session = get_session()
    txt = db_get_msg(text_name, session).text_value.replace("\\n", "\n")
    return txt


def add_account_payment(result: ApiPaymentResult):
    account_id = result.account_id
    session = get_session()
    account = db_get_account(account_id, session)
    # update account
    payed_events = account.payed_events + result.payed_events
    db_update_account(account_id, session, payed_events=payed_events)
    # insert payment
    data = {
        'payment_date': date.today(),
        'payed_events': result.payed_events,
        'payment_sum': result.payed_sum,
        'transaction_id': result.transaction_id
    }
    db_insert_payment(account_id, session, **data)


def about_fund_info(fund_id) -> str:
    """
    Сформировать экран приветствия донора, анонимного донора
    :param fund_id:
    :return:
    """
    session = get_session()
    fund: Fundraising = db_get_fundraising(fund_id, session)
    account = db_get_account(fund.account_id, session)
    user_name = account.user.name

    # разобрать поле gift_info на список ссылок
    gift_info = fund.gift_info
    try:
        gift_links = json.loads(gift_info)
        gift_links = '\n'.join(gift_links.values())
    except JSONDecodeError:
        gift_links = gift_info

    msg = f'Вас пригласил {user_name}, чтобы подготовить подарок.\n\n'
    msg += f'Тип события: {fund.reason}\n' if fund.reason else ''
    msg += f'Кому собираем: {fund.target}\n' if fund.target else ''
    msg += f'Дата события: {fund.event_date}\n' if fund.event_date else ''
    msg += f'Варианты подарков: {gift_links}\n' if gift_info else ''
    msg += f'Дата поздравления: {fund.congratulation_date}\n' if fund.congratulation_date else ''
    msg += f'Время: {fund.congratulation_time}\n' if fund.congratulation_time else ''
    msg += f'Где поздравляем: {fund.event_place}\n' if fund.event_place else ''
    msg += f'Дресс-код: {fund.event_dresscode}\n' if fund.event_dresscode else ''
    return msg


def transfer_fund_info(fund_id) -> str:
    session = get_session()
    fund: Fundraising = db_get_fundraising(fund_id, session)
    avg_sum = db_get_fund_avg_sum(fund_id, session)

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
    fund: Fundraising = db_get_fundraising(fund_id, session)
    donors = [d for d in fund.donors if d.user_id == user_id]
    if len(donors) == 0:
        user = db_insert_user(user_id, session, name=user_name)
        donor: Donor = db_insert_donor(fund_id, user_id, session)
    else:
        donor: Donor = donors[0]
    donor.payed += sum_money
    donor.payed_date = date.today()
    session.commit()
    return True
