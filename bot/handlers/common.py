import json
from queue import Queue

from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.utils.exceptions import MessageToDeleteNotFound

import db
from backend import FundraisingInfo, Account, PaymentResult, UserInfo, ApiUserStatus
from config import Config
from db.bl import UserStatus
from utils import is_number, calc_payment_sum

bot_config = Config()

msgs = Queue()  #


class Steps(StatesGroup):
    tg_2 = State()
    tg_3 = State()
    tg_4 = State()
    tg_5 = State()
    tg_6 = State()
    tg_7 = State()
    tg_8 = State()
    tg_9 = State()
    tg_10 = State()
    tg_11 = State()
    tg_12 = State()
    tg_13 = State()  # форма главного меню TrialUser
    tg_14 = State()
    tg_15 = State()
    tg_16 = State()
    tg_17 = State()
    tg_18 = State()
    tg_19 = State()  # форма главного меню User
    s_1 = State()    # экран приветствия донора
    s_11 = State()   # экран приветствия анонимного донора
    s_2 = State()
    s_3 = State()    # экран с информацией о карте для приема денег
    s_4 = State()    # экран для ввода суммы перевода
    s_5 = State()    # экран где благодарим за перевод
    s_6 = State()    # экран после регистрации анонимного донора

    cmd_create_chat = State()

    fund_info = State()
    reg_company = State()


async def del_msg(message: types.Message):
    try:
        await message.delete()
    except MessageToDeleteNotFound:
        pass


async def _remove_all_messages(chat_id: int):
    while not msgs.empty():
        m = msgs.get()
        if type(m) == types.Message and m.chat.id == chat_id:
            try:
                await m.delete()
            except MessageToDeleteNotFound as ex:
                pass


def visitor_keyboard():
    url1 = f'{bot_config.base_url}UserRegistration'
    url2 = f'{bot_config.base_url}CompanyRegistration'
    buttons = [
        InlineKeyboardButton(text="Организовать сбор на подарок", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Зарегистрировать компанию", web_app=types.WebAppInfo(url=url2)),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def create_fund_keyboard(account_id: int, payed_events: int):
    url1 = f'{bot_config.base_url}CreateFund/?account_id={account_id}&payed_events={payed_events}'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    buttons = [
        InlineKeyboardButton(text="Организовать сбор на подарок", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Зарегистрировать компанию", web_app=types.WebAppInfo(url=url2)),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def home_button():
    buttons = ['В меню']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, one_time_keyboard=False)
    keyboard.add(*buttons)
    return keyboard


def payment_keyboard(account_id: int, cnt: int):
    url = f'{bot_config.base_url}payment/{account_id}/{cnt}'

    buttons = [
        InlineKeyboardButton(text="Оплатить", url=url),
        InlineKeyboardButton(text="В меню", callback_data='go_menu')
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def payment_keyboard_1():
    """
    вызывается из tg_7
    """
    buttons = [
        InlineKeyboardButton(text="Оплатить", callback_data='start_pay')
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def go_back_keyboard():
    buttons = [
        InlineKeyboardButton(text="Назад", callback_data='go_back')
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def go_menu_keyboard():
    buttons = [
        InlineKeyboardButton(text="В меню", callback_data='go_menu')
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def trial_user_menu_keyboard():
    buttons = [
        InlineKeyboardButton(text="Перейти к сбору", callback_data='fund_info'),
        InlineKeyboardButton(text="Чаты", callback_data='chat'),
        InlineKeyboardButton(text="Оплатить тариф и создать новый сбор", callback_data='start_pay'),
        InlineKeyboardButton(text="Зарегистрировать компанию", callback_data='None'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def user_menu_keyboard(user_id: int, account_id: int, payed_events: int):
    url1 = f'{bot_config.base_url}account/{account_id}/funds/'
    url2 = f'{bot_config.base_url}CreateFund/?account_id={account_id}&payed_events={payed_events}'
    url3 = f'{bot_config.base_url}user/{user_id}'
    buttons = [
        InlineKeyboardButton(text="Ваши сборы", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Создать новый сбор", web_app=types.WebAppInfo(url=url2)),
        InlineKeyboardButton(text="Редактировать анкету", web_app=types.WebAppInfo(url=url3)),
        InlineKeyboardButton(text="Чаты", callback_data='chat'),
        InlineKeyboardButton(text="Зарегистрировать компанию", callback_data='None'),
        # InlineKeyboardButton(text="Переключить аккаунт", callback_data='None'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def anonymous_donor_menu():
    url1 = f'{bot_config.base_url}UserRegistration'
    buttons = [
        InlineKeyboardButton(text="Заполнить анкету", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Участвовать в сборе без регистрации", callback_data='accept_fund'),
        InlineKeyboardButton(text="Отклонить предложение", callback_data='decline_offer'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def donor_menu():
    buttons = [
        InlineKeyboardButton(text="Принять предложение", callback_data='accept_fund'),
        InlineKeyboardButton(text="Отклонить предложение", callback_data='decline_offer'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def decline_offer_menu():
    url1 = f'{bot_config.base_url}UserRegistration'
    buttons = [
        InlineKeyboardButton(text="Заполнить анкету", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Участвовать в сборе без регистрации", callback_data='accept_fund'),
        InlineKeyboardButton(text="Покинуть сбор", callback_data='go_menu'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def decline_offer_menu2():
    buttons = [
        InlineKeyboardButton(text="Принять предложение", callback_data='accept_fund'),
        InlineKeyboardButton(text="Покинуть сбор", callback_data='go_menu'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def sent_money_menu():
    buttons = [
        InlineKeyboardButton(text="Отправил", callback_data='sent_money'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def new_private_fund_keyboard(account_id: int, payed_events: int):
    url1 = f'{bot_config.base_url}CreateFund/?account_id={account_id}&payed_events={payed_events}'
    buttons = [
        InlineKeyboardButton(text="Создать сбор", web_app=types.WebAppInfo(url=url1)),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def open_fund_info_keyboard(state: FSMContext):
    user_data = await state.get_data()
    fund_id = user_data['fund_id']
    url1 = f'{bot_config.base_url}fundraising/{fund_id}'
    url2 = f'{bot_config.base_url}donors/edit/{fund_id}'
    url3 = f'{bot_config.base_url}donors/{fund_id}'
    buttons = [
        InlineKeyboardButton(text="Ссылка на сбор", callback_data='show_fund_link'),
        InlineKeyboardButton(text="Изменить детали сбора", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Редактировать список участников", web_app=types.WebAppInfo(url=url2)),
        InlineKeyboardButton(text="Детали сбора", web_app=types.WebAppInfo(url=url3)),
        InlineKeyboardButton(text="В меню", callback_data='go_menu'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def closed_fund_info_keyboard(state: FSMContext):
    user_data = await state.get_data()
    fund_id = user_data['fund_id']
    url1 = f'{bot_config.base_url}donors/{fund_id}'
    buttons = [
        InlineKeyboardButton(text="Детали сбора", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="В меню", callback_data='go_menu'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def send_message(chat_id, text, **kwargs):
    bot = Bot.get_current()
    _msg = await bot.send_message(chat_id, text, **kwargs)
    return _msg


async def start_visitor(user_id: int, state: FSMContext):
    await _remove_all_messages(user_id)

    msg = db.get_message_text('start_message')
    keyboard = visitor_keyboard()
    _msg = await send_message(user_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)
    await state.set_state(Steps.tg_2)


async def start_trial_user(user_id, state: FSMContext):
    await _remove_all_messages(user_id)

    fund_id = db.get_trial_fund_id(user_id)
    account: Account = db.get_api_user_account(user_id)
    await state.update_data(user_id=user_id)
    await state.update_data(account_id=account.id)
    await state.update_data(fund_id=fund_id)

    name = db.get_user_name(user_id)
    if fund_id is not None:
        keyboard = trial_user_menu_keyboard()
        msg = f'Здравствуйте, {name}!\nЗдесь вы можете управлять бесплатным сбором и продолжать общение со мной\n\n'
        msg = db.get_message_text('trial_menu').format(name=name)
        await state.set_state(Steps.tg_13)
    else:
        account: Account = db.get_api_user_account(user_id)
        keyboard = create_fund_keyboard(account.id, account.payed_events)   # идем по пути Посетителя
        msg = db.get_message_text('start_message')
        await state.set_state(Steps.tg_3)

    _msg = await send_message(user_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_user(user_id: int, state: FSMContext):
    await _remove_all_messages(user_id)
    name = db.get_user_name(user_id)
    user_info: UserInfo = db.get_user_info(user_id)
    msg = f'Здравствуйте, {name}!\nЗдесь вы можете оценить свою активность\n\n' \
          f'Участие в сборах: {user_info.donors_count}\n' \
          f'Создано сборов: {user_info.funds_count}\n' \
          f'Участвуете в компаниях: {user_info.company_count}\n' \
          f'Открытые сборы: {user_info.open_funds}\n' \
          f'Администратор компаний: {user_info.admin_count}'
    account: Account = db.get_api_user_account(user_id)
    keyboard = user_menu_keyboard(user_id, account.id, account.payed_events)

    await state.set_state(Steps.tg_19)
    _msg = await send_message(user_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_admin(user_id: int):
    await _remove_all_messages(user_id)
    msg = db.get_message_text('start_message')
    keyboard = admin_menu_keyboard()
    _msg = await send_message(user_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_anonymous_donor(chat_id: int, args: str, state: FSMContext):
    user_id = chat_id
    await _remove_all_messages(user_id)
    fund_id = args.replace('fund_', '')
    await state.update_data(fund_id=fund_id)

    msg = db.about_fund_info(fund_id)
    msg += '\nПожалуйста, заполните анкету для регистрации.\n'
    msg += '\nТак вы сможете участвовать в других сборах, а я напомню друзьям, когда у вас день рождения.'
    keyboard = anonymous_donor_menu()

    await state.set_state(Steps.s_11)
    bot = Bot.get_current()
    _msg = await bot.send_message(chat_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_donor(user_id: int, args, state: FSMContext):
    await _remove_all_messages(user_id)
    fund_id = args.replace('fund_', '')
    await state.update_data(fund_id=fund_id)

    msg = f'Здравствуйте.\nНапомню, что я - Дружба, бот-помощник для сбора на подарки.\n\n'
    msg += db.about_fund_info(fund_id)
    keyboard = donor_menu()

    await state.set_state(Steps.s_1)
    _msg = await send_message(user_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def cmd_start(message: types.Message, state: FSMContext):
    """
    Точка входа в бот
    """
    await del_msg(message)
    await state.finish()

    args = message.get_args()
    has_invite_url = args is not None and len(args) > 0

    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    user_status = UserStatus.Unknown
    statuses: list[ApiUserStatus] = db.get_user_statuses(user_id, has_invite_url=has_invite_url)
    if statuses[0].status == 'AnonymousDonor':
        user_status = UserStatus.AnonymousDonor
    elif statuses[0].status == 'Donor':
        user_status = UserStatus.Donor
    elif statuses[0].status == 'Visitor':
        user_status = UserStatus.Visitor
    elif statuses[0].status == 'TrialUser':
        user_status = UserStatus.TrialUser
    elif statuses[0].status == 'User':
        user_status = UserStatus.User
    elif statuses[0].status == 'Admin':
        user_status = UserStatus.Admin

    await state.update_data(user_status=user_status)

    if user_status == UserStatus.Visitor:
        await start_visitor(user_id, state)
        return

    if user_status == UserStatus.TrialUser:
        await start_trial_user(user_id, state)
        return

    if user_status == UserStatus.User:
        await start_user(user_id, state)
        return

    if user_status == UserStatus.Admin:
        await message.answer(f'user_status={user_status}, находится в разработке')
        return

    if user_status == UserStatus.Donor:
        await start_donor(user_id, args, state)
        return

    if user_status == UserStatus.AnonymousDonor:
        await start_anonymous_donor(user_id, args, state)
        return

    await message.answer(f'Ошибка, не удалось определить статус пользователя (user_status={user_status})')


async def cmd_reset(message: types.Message, state: FSMContext):
    await del_msg(message)
    await state.finish()
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    db.remove_user(user_id)
    msg = f'Данные о пользователе @{user_name} ({first_name} {last_name}) были удалены из базы данных бота Дружба'
    await message.answer(msg)


async def cmd_reset_payments(message: types.Message, state: FSMContext):
    await del_msg(message)
    await state.finish()
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    db.remove_user_payments(user_id)
    msg = f'Данные о платежах пользователя @{user_name} ({first_name} {last_name}) ' \
          f'были удалены из базы данных бота Дружба'
    await message.answer(msg)


async def query_start(call: types.CallbackQuery):
    await cmd_start(call.message, "*")


async def open_fund_info(message: types.Message, fund_id: int, state: FSMContext) -> types.Message:
    """
    Показать информацию по открытому сбору
    """
    await del_msg(message)
    await _remove_all_messages(message.chat.id)
    fi: FundraisingInfo = db.get_fund_info(fund_id)
    await state.update_data(invite_url=fi.invite_url)
    await state.update_data(fund_target=fi.target)
    await state.update_data(fund_reason=fi.reason)
    msg = fi.msg()
    keyboard = await open_fund_info_keyboard(state)
    await state.set_state(Steps.tg_16)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    return _msg


async def closed_fund_info(message: types.Message, fund_id: int, state: FSMContext) -> types.Message:
    """
    Показать информацию по закрытому сбору
    """
    await del_msg(message)
    fi: FundraisingInfo = db.get_fund_info(fund_id)
    await state.update_data(invite_url=fi.invite_url)
    msg = fi.msg()
    keyboard = await closed_fund_info_keyboard(state)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(Steps.tg_15)
    return _msg


async def query_fund_info(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    user_id = call.from_user.id
    user_data = await state.get_data()
    user_status = user_data.get('user_status')

    if user_status == UserStatus.TrialUser:
        fund_id = user_data.get('fund_id')

        is_fund_open = db.is_fund_open(fund_id)
        if is_fund_open:
            return await open_fund_info(call.message, fund_id, state)
        return await closed_fund_info(call.message, fund_id, state)

    if user_status == UserStatus.User:
        fund_id = user_data.get('fund_id')

        await db.start_fund(fund_id)
        is_fund_open = db.is_fund_open(fund_id)
        if is_fund_open:
            return await open_fund_info(call.message, fund_id, state)
        return await closed_fund_info(call.message, fund_id, state)


async def create_user_account(message: types.Message, account_id: int, state: FSMContext):
    await state.update_data(account_id=account_id)
    await state.update_data(user_status=UserStatus.TrialUser)

    keyboard = new_private_fund_keyboard(account_id, 1)
    msg = 'Ура, вы успешно зарегистрировались!\nДавайте перейдем к созданию сбора на подарок'
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)
    await state.set_state(Steps.tg_3)


async def create_company_account(message: types.Message, company_id: int, company_account_id: int, state: FSMContext):
    await state.update_data(account_id=company_account_id)
    await state.update_data(user_status=UserStatus.TrialUser)

    company = db.get_company(company_id)
    company_url = db.create_company_url(company_id)
    user_id = message.from_user.id
    user_name = db.get_user_name(user_id)

    msg = f'Поздравляю, вы успешно подключили компанию к сервису. Теперь мы дружим:) \n\n' \
          f'Скопируйте эту ссылку вместе с текстом сообщения и отправьте друзьям или коллегам, которые будут ' \
          f'участвовать в сборах вашей компании. Они внесут свои данные, и я смогу автоматически напоминать ' \
          f'им о событиях, получать информацию о переводах и передавать её вам.'
    _msg = await message.answer(msg)
    msgs.put(_msg)

    keyboard = payment_keyboard_1()
    msg = f'Здравствуйте! <b>{user_name}</b> из компании <b>{company.name}</b>  приглашает вас в сервис Дружба, ' \
          f'чтобы вместе участвовать в сборах на подарки друзьям и коллегам. Присоединяйтесь! \n' \
          f'{company_url}'
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)
    await state.set_state(Steps.tg_7)


async def webapp_visitors(message: types.Message, state: FSMContext):
    # state == Steps.reg_visitor
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if answer['command'] == 'create_user':
        if 'account_id' in answer:
            account_id = answer['account_id']
            await create_user_account(message, account_id, state)
        else:
            _msg = await message.answer("Не удалось зарегистрировать пользователя. Попробуйте снова")
            msgs.put(_msg)
        return

    if answer['command'] == 'create_company':
        company_id = answer['company_id']
        company_account_id = answer['company_account_id']
        member_account_id = answer['member_account_id']
        create_company_account(message, company_id, company_account_id, state)


async def webapp_user_operation(message: types.Message, state: FSMContext):
    # state == [Steps.tg_19]
    await _remove_all_messages(message.from_user.id)
    items = message.text.split('&')
    answer = json.loads(items[1])
    operation = answer.get('operation', '')
    if operation == 'create_fund':
        return await webapp_create_user_fund(message, state)
    elif operation == 'open_fund':
        fund_id = answer.get('fund_id', '')
        account_id = answer.get('account_id', '')
        await state.update_data(fund_id=fund_id)
        await state.update_data(account_id=account_id)

        db.start_fund(fund_id)
        is_fund_open = db.is_fund_open(fund_id)
        if is_fund_open:
            return await open_fund_info(message, fund_id, state)
        return await closed_fund_info(message, fund_id, state)


async def webapp_create_user_fund(message: types.Message, state: FSMContext):
    # state == [Steps.tg_3]
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    account_id = answer['account_id']
    fund_id = answer['fund_id']
    await state.update_data(account_id=account_id)
    await state.update_data(fund_id=fund_id)

    if 'fund_id' in answer:
        invite_url = answer.get('invite_url', '')
        target = answer.get('target', '')
        reason = answer.get('reason', '')
        if len(invite_url) > 0:
            await state.update_data(invite_url=invite_url)
            await state.update_data(target=target)
            await state.update_data(reason=reason)
            await show_fund_success(message, state)
        else:
            await start_payment(message, state)
    else:
        _msg = await message.answer("Не удалось зарегистрировать пробный сбор.")
        msgs.put(_msg)


async def show_fund_success(message: types.Message, state: FSMContext):
    await del_msg(message)
    user_data = await state.get_data()
    invite_url = user_data.get('invite_url', '')
    target = user_data.get('target')
    reason = user_data.get('reason')

    msg = f'Всё получилось — вы успешно создали сбор.\n' \
          f'Скопируйте эту ссылку и отправьте друзьям или коллегам. Пусть каждый внесёт свой вклад в поздравление:)\n' \
          f'\nСами можете тоже поучаствовать в сборе по этой ссылке.'
    await state.set_state(Steps.tg_4)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML)
    msgs.put(_msg)

    keyboard = go_menu_keyboard()
    msg = f'Здравствуйте! {target} скоро празднует {reason}.\nЭто ссылка для сбора на подарок. Присоединяйтесь!\n' \
          f'{invite_url}'

    await state.set_state(Steps.tg_5)
    await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def show_fund_link(message: types.Message, state: FSMContext):
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)
    user_data = await state.get_data()

    invite_url = user_data['invite_url']
    target = user_data['target']
    reason = user_data['reason']

    keyboard = go_back_keyboard()
    msg = f'Здравствуйте! {target} скоро {reason}.\nЭто ссылка для сбора на подарок.Присоединяйтесь!\n' \
          f'{invite_url}'

    await state.set_state(Steps.tg_5)
    await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def show_main_menu(message: types.Message, state: FSMContext):
    await del_msg(message)

    statuses: list[ApiUserStatus] = db.get_user_statuses(message.from_user.id, has_invite_url=False)
    user_status = statuses[0]
    await state.update_data(user_status=user_status)

    await start_trial_user(message, state)


async def query_show_main_menu(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await show_main_menu(call.message, state)


async def query_show_invite_link_continue(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    # await call.message.delete()
    user_data = await state.get_data()
    # все данные о пользователе
    user_status = user_data['user_status']
    account_id = user_data['account_id']
    fund_id = user_data['fund_id']
    invite_url = user_data['invite_url']
    await open_fund_info(call.message, fund_id, state)


async def query_show_fund_link(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    # tg_17, tg_18
    await call.message.delete()
    user_data = await state.get_data()
    invite_url = user_data.get('invite_url', None)
    fund_target = user_data.get('fund_target', None)
    reason = user_data.get('fund_reason', None)

    msg = f'Спасибо, что выбрали Дружбу!\n' \
          f'Скопируйте эту ссылку и отправьте друзьям или коллегам.\n' \
          f'Пусть каждый внесёт свой вклад в поздравление :)'
    _msg = await call.message.answer(msg)
    msgs.put(_msg)

    keyboard = go_back_keyboard()
    msg = f'Здравствуйте! {fund_target} скоро празднует {reason}.\nЭто ссылка для сбора на подарок. Присоединяйтесь!' \
          f'\n{invite_url}'
    await call.message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    return


async def query_return_menu(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await call.message.delete()
    await state.finish()

    user_status = UserStatus.Unknown
    user_id = call.from_user.id
    await state.update_data(user_id=user_id)
    statuses: list[ApiUserStatus] = db.get_user_statuses(user_id, has_invite_url=False)
    if statuses[0].status == 'Visitor':
        user_status = UserStatus.Visitor
    elif statuses[0].status == 'TrialUser':
        user_status = UserStatus.TrialUser
    elif statuses[0].status == 'User':
        user_status = UserStatus.User
    elif statuses[0].status == 'Admin':
        user_status = UserStatus.Admin
    elif statuses[0].status == 'AnonymousDonor':
        user_status = UserStatus.AnonymousDonor
    elif statuses[0].status == 'Donor':
        user_status = UserStatus.Donor

    await state.update_data(user_status=user_status)

    if user_status == UserStatus.Visitor:
        await start_visitor(user_id, state)
    elif user_status == UserStatus.TrialUser:
        await start_trial_user(user_id, state)
    elif user_status == UserStatus.User:
        await start_user(user_id, state)
    elif user_status == UserStatus.Admin:
        await start_admin(user_id)


async def start_payment(message: types.Message, state: FSMContext):
    await del_msg(message)
    user_id = message.from_user.id
    user_data: dict = await state.get_data()
    user_status: UserStatus = user_data.get('user_status')
    account_id = user_data.get('account_id')

    keyboard = go_menu_keyboard()
    available_funds = db.get_available_funds(account_id)
    tariff_name = db.get_current_tariff(account_id)
    msg = f'Сейчас у вас подключен тариф: {tariff_name} \n\nДоступные сборы: {available_funds}\n\n\n' \
          f'Введите количество сборов, которые хотите оплатить'
    await state.set_state(Steps.tg_8)

    photo = open('bot/images/tariffs.jpg', 'rb')
    _msg = await message.answer_photo(photo, caption=msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def query_start_payment(call: types.CallbackQuery, state: FSMContext):
    """
    Start the payment process
    """
    await start_payment(call.message, state)


async def payment_step_2(message: types.Message, state: FSMContext):
    # state tg_8
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)

    ok = is_number(message.text)
    if not ok:
        await start_payment(message, state)
        return

    fund_count = int(message.text)
    user_data = await state.get_data()
    account_id = user_data['account_id']
    payment_sum = calc_payment_sum(fund_count)
    keyboard = payment_keyboard(account_id, fund_count)
    # await state.update_data(fund_count=fund_count)
    msg = f'Количество сборов: {fund_count}\n' \
          f'Стоимость составит {payment_sum} руб.\n\n' \
          f'Нажмите «Оплатить» или введите другое количество сборов.'
    await state.set_state(Steps.tg_9)
    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


async def payment_step_3(message: types.Message, state: FSMContext):
    result: PaymentResult = json.loads(message.text)
    if result.success:
        user_data = await state.get_data()
        await state.update_data(payed_events=result.payed_events)
        await show_payment_success(message, state)
    else:
        await show_payment_error(message, state)


async def show_payment_success(message: types.Message, state: FSMContext):
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)
    keyboard = go_menu_keyboard()

    user_data = await state.get_data()
    payed_events = user_data.get('payed_events')
    msg = f'Поздравляю! Вы успешно приобрели пакет из {payed_events} сборов.\n' \
          f'Теперь можно начинать готовиться к праздникам 🙂\n\nСпасибо, что выбрали Дружбу!'
    await state.set_state(Steps.tg_11)

    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


async def show_payment_error(message: types.Message, state: FSMContext):
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)

    user_data = await state.get_data()
    account_id = user_data.get('account_id')
    payed_events = user_data.get('payed_events')

    keyboard = payment_keyboard(account_id, payed_events)
    msg = f'К сожалению, оплата не прошла. Давайте попробуем ещё раз.'
    await state.set_state(Steps.tg_9)

    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


async def query_decline_offer(call: types.CallbackQuery, state: FSMContext):
    """
    User click <Отклонить предложение> on anonymous_donor_menu or donor_menu
    """
    await call.message.delete()
    user_data = await state.get_data()
    user_status: UserStatus = user_data.get('user_status')

    keyboard = None
    if user_status == UserStatus.AnonymousDonor:
        keyboard = decline_offer_menu()
    if user_status == UserStatus.Donor:
        keyboard = decline_offer_menu2()

    await state.set_state(Steps.s_11)
    msg = 'Вы отказались от участия в сборе.\nВозможно, случайно.\n\nХотите принять приглашение и начать участвовать?'
    _msg = await call.message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def query_accept_fund(call: types.CallbackQuery, state: FSMContext):
    """
    Участвовать в сборе (без регистрации)
    """
    await call.message.delete()
    user_id = call.message.chat.id
    user_data = await state.get_data()
    fund_id = user_data.get('fund_id')

    keyboard = sent_money_menu()
    msg = db.transfer_fund_info(fund_id)

    await state.set_state(Steps.s_3)
    _msg = await call.message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def webapp_reg_user(message: types.Message, state: FSMContext):
    """
    Участвовать в сборе после регистрации анонимного донора. Он уже просто донор
    :param message:
    :param state:
    :return:
    """
    # state s_11
    await del_msg(message)
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if 'account_id' not in answer:
        return

    user_data = await state.get_data()
    fund_id = user_data.get('fund_id')

    keyboard = sent_money_menu()
    msg = 'Ура, вы успешно зарегистрировались.\n\n' + db.transfer_fund_info(fund_id)

    await state.set_state(Steps.s_6)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def query_sent_money(call: types.CallbackQuery, state: FSMContext):
    """
    вводим сумму перевода
    """
    await call.message.delete()
    user_data = await state.get_data()
    msg = 'Пожалуйста, введите сумму, которую вы перевели для того, чтобы я ее учла.'
    await state.set_state(Steps.s_4)
    _msg = await call.message.answer(msg, parse_mode=ParseMode.HTML)
    msgs.put(_msg)


async def sent_money_2(message: types.Message, state: FSMContext):
    # state s_4
    await del_msg(message)
    await _remove_all_messages(message.chat.id)

    ok = is_number(message.text)
    if not ok:
        _msg = await message.answer('Нужно ввести число, попробуйте еще раз.')
        msgs.put(_msg)
        return

    user_id = message.from_user.id
    user_data = await state.get_data()
    fund_id = user_data.get('fund_id')
    sum_money = int(message.text)
    user_name = f'{message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username})'
    db.save_money_transfer(fund_id, user_id, user_name, sum_money)

    keyboard = go_menu_keyboard()
    msg = f'Спасибо, вы отличный друг!'
    await state.set_state(Steps.s_5)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def query_edit_user(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Операция редактирования анкеты пользователя находится в разработке')


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_reset, commands="reset", state="*")
    dp.register_message_handler(cmd_reset_payments, commands="reset_payments", state="*")

    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_show_fund_link, lambda c: c.data == 'show_fund_link', state="*")
    dp.register_callback_query_handler(query_return_menu, lambda c: c.data == 'go_menu', state="*")
    dp.register_callback_query_handler(query_fund_info, lambda c: str(c.data).startswith('fund_info'), state="*")

    dp.register_message_handler(webapp_visitors, filters.Text(startswith='webapp'), state=Steps.tg_2)
    dp.register_message_handler(webapp_create_user_fund, filters.Text(startswith='webapp'), state=[Steps.tg_3])
    dp.register_message_handler(webapp_user_operation, filters.Text(startswith='webapp'), state=[Steps.tg_19])

    dp.register_message_handler(webapp_reg_user, filters.Text(startswith='webapp'),
                                state=[Steps.s_11, Steps.s_2])

    dp.register_callback_query_handler(query_show_invite_link_continue, lambda c: c.data == 'go_back',
                                       state=Steps.tg_16)
    dp.register_callback_query_handler(query_show_main_menu, lambda c: c.data == 'go_back',
                                       state=Steps.tg_5)

    dp.register_callback_query_handler(query_start_payment, lambda c: c.data == 'start_pay', state='*')

    dp.register_message_handler(show_main_menu, lambda message: message.text == 'В меню', state='*')

    dp.register_message_handler(payment_step_2, state=[Steps.tg_8, Steps.tg_9])

    dp.register_message_handler(show_fund_link, state=Steps.tg_4)

    dp.register_message_handler(payment_step_3, state=Steps.tg_9)

    dp.register_callback_query_handler(query_decline_offer, lambda c: c.data == 'decline_offer',
                                       state=[Steps.s_1, Steps.s_11])

    dp.register_callback_query_handler(query_accept_fund, state=[Steps.s_1, Steps.s_2, Steps.s_11])

    dp.register_callback_query_handler(query_sent_money, state=[Steps.s_3, Steps.s_6])

    dp.register_message_handler(sent_money_2, state=Steps.s_4)

    dp.register_callback_query_handler(query_edit_user, lambda c: c.data == 'edit_user', state='*')
