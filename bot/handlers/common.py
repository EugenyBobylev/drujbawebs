import json
from queue import Queue

from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.utils.exceptions import MessageToDeleteNotFound

import db
from backend import FundraisingInfo, Account, PaymentResult, UserInfo
from config import Config
from db.bl import get_session, UserStatus
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

    fund_info = State()
    reg_company = State()


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
        InlineKeyboardButton(text="Переключить аккаунт", callback_data='None'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def user_menu_keyboard():
    buttons = [
        InlineKeyboardButton(text="Ваши сборы", callback_data='funds_info'),
        InlineKeyboardButton(text="Создать новый сбор", callback_data='create_fund'),
        InlineKeyboardButton(text="Редактировать анкету", callback_data='edit_user'),
        InlineKeyboardButton(text="Чаты", callback_data='chat'),
        InlineKeyboardButton(text="Зарегистрировать компанию", callback_data='None'),
        InlineKeyboardButton(text="Переключить аккаунт", callback_data='None'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def new_private_fund_keyboard():
    url1 = f'{bot_config.base_url}FeeCreation'
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
        InlineKeyboardButton(text="Закрыть", callback_data='return_menu'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def start_visitor(message: types.Message, state: FSMContext):
    # user_data = await state.get_data()
    # user_status = user_data['user_status']

    msg = db.get_message_text('start_message')
    keyboard = visitor_keyboard()
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)
    await state.set_state(Steps.tg_2)


async def start_trial_user(message: types.Message, state: FSMContext):
    await _remove_all_messages(message.chat.id)
    # await message.delete()
    name = db.get_user_name(message.chat.id)
    msg = db.get_message_text('trial_menu').format(name=name)
    keyboard = trial_user_menu_keyboard()

    await state.set_state(Steps.tg_13)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_user(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    await _remove_all_messages(user_id)
    name = db.get_user_name(user_id)
    user_info: UserInfo = db.get_user_info(user_id)
    msg = f'Здравствуйте, {name}!\nЗдесь вы можете оценить свою активность\n\n' \
          f'Участие в сборах: {user_info.donors_count}\n' \
          f'Создано сборов: {user_info.funds_count}\n' \
          f'Участвуете в компаниях: {user_info.company_count}\n' \
          f'Открытые сборы: {user_info.open_funds}\n' \
          f'Администратор компаний: {user_info.admin_count}'
    keyboard = user_menu_keyboard()

    await state.set_state(Steps.tg_19)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def cmd_start(message: types.Message, state: FSMContext):
    """
    Точка входа в бот
    """
    await message.delete()
    await state.finish()
    session = get_session()

    user_id = message.from_user.id
    user_status: UserStatus = db.get_user_status(user_id, account_id=None, has_invite_url=False)
    await state.update_data(user_status=user_status)
    if user_status == UserStatus.Visitor:
        await start_visitor(message, state)
        return

    if user_status == UserStatus.TrialUser:
        fund_id = db.get_trial_fund_id(user_id)
        account: Account = db.get_api_user_account(user_id)
        await state.update_data(account_id=account.id)
        await state.update_data(fund_id=fund_id)
        await start_trial_user(message, state)
        return

    if user_status == UserStatus.User:
        await start_user(message, state)
        return

    if user_status == UserStatus.Admin:
        await message.answer(f'user_status={user_status}, находится в разработке')
        return
    if user_status == UserStatus.Donor:
        await message.answer(f'user_status={user_status}, находится в разработке')
        return
    if user_status == UserStatus.AnonymousDonor:
        await message.answer(f'user_status={user_status}, находится в разработке')
        return
    await message.answer(f'Ошибка, не удалось определить статус пользователя (user_status={user_status})')
    return


async def query_start(call: types.CallbackQuery):
    await cmd_start(call.message, "*")


async def open_fund_info(message: types.Message, fund_id: int, state: FSMContext) -> types.Message:
    """
    Показать информацию по открытому сбору
    """
    await message.delete()
    await _remove_all_messages(message.chat.id)
    fi: FundraisingInfo = db.get_fund_info(fund_id)
    await state.update_data(invite_url=fi.invite_url)
    await state.update_data(fund_target=fi.target)
    msg = fi.msg()
    keyboard = await open_fund_info_keyboard(state)
    await state.set_state(Steps.tg_16)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    return _msg


async def closed_fund_info(message: types.Message, fund_id: int, state: FSMContext) -> types.Message:
    """
    Показать информацию по закрытому сбору
    """
    await message.delete()
    fi: FundraisingInfo = db.get_fund_info(fund_id)
    await state.update_data(invite_url=fi.invite_url)
    msg = fi.msg()
    keyboard = await closed_fund_info_keyboard(state)
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(Steps.tg_15)
    return _msg


async def query_fund_info(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    user_data = await state.get_data()
    user_status = user_data['user_status']

    if user_status == UserStatus.TrialUser:
        user_id = call.from_user.id
        fund_id = db.get_trial_fund_id(user_id)
        if fund_id is None:
            await call.message.delete()
            return await call.message.answer(f'Ошибка. Пробный сбор не найден (user_id={user_id}, fund_id={fund_id}).')

        await state.update_data(fund_id=fund_id)
        is_fund_open = db.is_fund_open(fund_id)
        if is_fund_open:
            return await open_fund_info(call.message, fund_id, state)
        return await closed_fund_info(call.message, fund_id, state)


async def webapp_create_user_account(message: types.Message, state: FSMContext):
    # state == Steps.reg_visitor
    await message.delete()
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if 'account_id' in answer:
        account_id = answer['account_id']
        await state.update_data(account_id=account_id)
        await state.update_data(user_status=UserStatus.TrialUser)

        keyboard = new_private_fund_keyboard()
        msg = 'Ура, вы успешно зарегистрировались!\nДавайте перейдем к созданию сбора на подарок'
        _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        msgs.put(_msg)
        await state.set_state(Steps.tg_3)
        return

    _msg = await message.answer("Не удалось зарегистрировать пользователя. Попробуйте снова")
    msgs.put(_msg)


async def webapp_create_user_fund(message: types.Message, state: FSMContext):
    # state == Steps.tg_3
    await message.delete()
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if 'fund_id' in answer:
        fund_id = answer['fund_id']
        invite_url = answer['invite_url']
        target = answer['target']
        await state.update_data(fund_id=fund_id)
        await state.update_data(invite_url=invite_url)

        msg = f'Поздравляю, вы успешно создали сбор!\nСкопируйте эту ссылку и текст сообщения и отправьте ' \
              f'друзьям или коллегам.\nПусть каждый внесёт свой вклад в поздравление {target}\n\n'
        await state.set_state(Steps.tg_4)
        _msg = await message.answer(msg, parse_mode=ParseMode.HTML)
        msgs.put(_msg)

        keyboard = go_menu_keyboard()
        msg = f'Здравствуйте! У {target} скоро день рождения.\nЭто ссылка для сбора на подарок.Присоединяйтесь!\n' \
              f'{invite_url}'

        await state.set_state(Steps.tg_5)
        await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return

    _msg = await message.answer("Не удалось зарегистрировать пробный сбор.")
    msgs.put(_msg)


async def show_fund_link(message: types.Message, state: FSMContext):
    await message.delete()
    await _remove_all_messages(message.from_user.id)
    user_data = await state.get_data()

    invite_url = user_data['invite_url']
    target = user_data['target']

    keyboard = go_back_keyboard()
    msg = f'Здравствуйте! У {target} скоро день рождения.\nЭто ссылка для сбора на подарок.Присоединяйтесь!\n' \
          f'{invite_url}'

    await state.set_state(Steps.tg_5)
    await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def show_main_menu(message: types.Message, state: FSMContext):
    await message.delete()
    user_data = await state.get_data()
    # все данные о пользователе
    exist_user_status = user_data['user_status']
    account_id = user_data['account_id']
    fund_id = user_data['fund_id']
    user_status = db.get_user_status(message.from_user.id, account_id=account_id, has_invite_url=False)
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
    await call.message.delete()
    user_data = await state.get_data()
    invite_url = user_data.get('invite_url', None)
    fund_target = user_data.get('fund_target', None)

    curr_state = await state.get_state()

    msg = f'Всё получилось — вы успешно создали сбор.\nСкопируйте эту ссылку и отправьте друзьям или коллегам. ' \
          f'Пусть каждый внесёт свой вклад в поздравление {fund_target}'
    _msg = await call.message.answer(msg)
    msgs.put(_msg)

    keyboard = go_back_keyboard()
    msg = f'Здравствуйте! У {fund_target} скоро день рождения. Это ссылка для сбор на подарок. Присоединяйтесь!' \
          f'\n{invite_url}'
    await call.message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    return


async def query_return_menu(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await call.message.delete()
    user_id = call.from_user.id
    user_data: dict = await state.get_data()
    user_status: UserStatus = user_data.get('user_status', None)
    if user_status is None:
        user_status = db.get_user_status(user_id, account_id=None, has_invite_url=False)
        await state.update_data(user_status=user_status)

    if user_status == UserStatus.TrialUser:
        await start_trial_user(call.message, state)
    elif user_status == UserStatus.User:
        await start_user(call.message, state)


async def start_payment(message: types.Message, state: FSMContext):
    await message.delete()
    user_id = message.from_user.id
    user_data: dict = await state.get_data()
    user_status: UserStatus = user_data.get('user_status')
    account_id = user_data.get('account_id')

    keyboard = go_menu_keyboard()
    available_funds = db.get_available_funds(account_id)
    msg = f'Сейчас у вас подключен тариф: \n\nДоступные сборы: {available_funds}\n\n\n' \
          f'Введите количество сборов, которые хотите оплатить:'
    await state.set_state(Steps.tg_8)
    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


async def query_start_payment(call: types.CallbackQuery, state: FSMContext):
    """
    Start the payment process
    """
    await start_payment(call.message, state)


async def payment_step_2(message: types.Message, state: FSMContext):
    # state tg_8
    await message.delete()
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
    msg = f'Стоимость {fund_count} сборов составит {payment_sum} руб.\n\n' \
          f'Нажмите «Оплатить» или введите другое количество сборов.'
    await state.set_state(Steps.tg_9)
    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


async def payment_step_3(message: types.Message, state: FSMContext):
    await message.delete()
    await _remove_all_messages(message.from_user.id)

    result: PaymentResult = json.loads(message.text)
    if result.success:
        keyboard = go_menu_keyboard()
        msg = f'Поздравляю! Вы успешно приобрели пакет из: {result.payed_events} сборов. ' \
              f'Теперь можно начинать готовиться к праздникам :)\n\nСпасибо, что выбрали Дружбу!'
        await state.set_state(Steps.tg_11)
    else:
        keyboard = payment_keyboard(result.account_id, result.payed_events)
        msg = f'К сожалению, оплата не прошла. Давайте попробуем ещё раз.'
        await state.set_state(Steps.tg_9)
    _msg = await message.answer(msg, reply_markup=keyboard)
    msgs.put(_msg)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_show_fund_link, lambda c: c.data == 'show_fund_link', state="*")
    dp.register_callback_query_handler(query_return_menu, lambda c: c.data == 'go_menu', state="*")

    # start_trial_user
    dp.register_callback_query_handler(query_fund_info, lambda c: c.data == 'fund_info', state="*")

    dp.register_message_handler(webapp_create_user_account, filters.Text(startswith='webapp'),
                                state=Steps.tg_2)
    dp.register_message_handler(webapp_create_user_fund, filters.Text(startswith='webapp'),
                                state=Steps.tg_3)
    dp.register_callback_query_handler(query_show_invite_link_continue, lambda c: c.data == 'go_back',
                                       state=Steps.tg_16)
    dp.register_callback_query_handler(query_show_main_menu, lambda c: c.data == 'go_back',
                                       state=Steps.tg_5)

    dp.register_callback_query_handler(query_start_payment, lambda c: c.data == 'start_pay', state='*')

    dp.register_message_handler(show_main_menu, lambda message: message.text == 'В меню', state='*')

    dp.register_message_handler(payment_step_2, state=[Steps.tg_8, Steps.tg_9])

    dp.register_message_handler(show_fund_link, state=Steps.tg_4)

    dp.register_message_handler(payment_step_3, state=Steps.tg_9)
