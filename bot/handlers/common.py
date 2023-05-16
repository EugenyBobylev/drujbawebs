import json
from queue import Queue

from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

import db
from backend import FundraisingInfo, User, Account
from config import BotConfig
from db.bl import get_session, get_msg, UserStatus

bot_config = BotConfig.instance()

msgs = Queue()  #


class Steps(StatesGroup):
    reg_visitor = State()
    create_fund = State()
    show_visitor_fund_link = State()
    show_fund_link = State()

    show_trial_user_menu = State()
    show_fund_info = State()

    reg_company = State()


async def _remove_all_messages(chat_id: int):
    while not msgs.empty():
        m = msgs.get()
        if type(m) == types.Message and m.chat.id == chat_id:
            await m.delete()


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


def show_invite_link_keyboard():
    buttons = [
        InlineKeyboardButton(text="Продолжить", callback_data='show_invite_link_continue')
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def trial_user_menu_keyboard():
    buttons = [
        InlineKeyboardButton(text="Перейти к сбору", callback_data='trial_fund_info'),
        InlineKeyboardButton(text="Чаты", callback_data='chat'),
        InlineKeyboardButton(text="Оплатить тариф и создать новый сбор", callback_data='pay'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def new_private_fund_keyboard():
    url1 = f'{bot_config.base_url}FeeCreation'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    buttons = [
        InlineKeyboardButton(text="Создать сбор", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Оплатить", web_app=types.WebAppInfo(url=url2)),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def fund_info_keyboard():
    buttons = [
        InlineKeyboardButton(text="Ссылка на сбор", callback_data='show_fund_link'),
        InlineKeyboardButton(text="Изменить детали сбора", callback_data='edit_fund'),
        InlineKeyboardButton(text="Редактировать список участников", callback_data='edit_fund_members'),
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
    await state.set_state(Steps.reg_visitor)


async def start_trial_user(message: types.Message, state: FSMContext):
    # await message.delete()
    name = db.get_user_name(message.chat.id)
    msg = db.get_message_text('trial_menu').format(name=name)
    keyboard = trial_user_menu_keyboard()
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(Steps.show_trial_user_menu)
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
        fund_id = db.get_trial_fund(user_id)
        account: Account = db.get_api_user_account(user_id)
        await state.update_data(account_id=account.id)
        await state.update_data(fund_id=fund_id)
        await start_trial_user(message, state)
        return

    if user_status == UserStatus.User:
        await message.answer(f'user_status={user_status}, находится в разработке')
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


async def fund_info(message: types.Message, fund_id: int, state: FSMContext) -> types.Message:
    """
    Показать информацию по сбору
    """
    await message.delete()
    fi: FundraisingInfo = db.get_fund_info(fund_id)
    await state.update_data(invite_url=fi.invite_url)
    msg = fi.msg()
    keyboard = fund_info_keyboard()
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(Steps.show_fund_info)
    return _msg


async def query_trial_fund_info(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    user_id = call.from_user.id
    fund_id = db.get_trial_fund(user_id)
    if fund_id is None:
        await call.message.delete()
        return await call.message.answer(f'Ошибка. Пробный сбор не найден (user_id={user_id}, fund_id={fund_id}).')
    return await fund_info(call.message, fund_id, state)


async def webapp_create_user_account(message: types.Message, state: FSMContext):
    # state == Steps.reg_visitor
    await message.delete()
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if 'account_id' in answer:
        account_id = answer['account_id']
        await state.update_data(account_id=account_id)

        keyboard = new_private_fund_keyboard()
        msg = 'Вы успешно зарегистрировались. Давайте продолжим.'
        _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        msgs.put(_msg)
        await state.set_state(Steps.create_fund)
        return

    _msg = await message.answer("Не удалось зарегистрировать пользователя. Попробуйте снова")
    msgs.put(_msg)


async def webapp_create_user_fund(message: types.Message, state: FSMContext):
    # state == Steps.create_fund
    await message.delete()
    await _remove_all_messages(message.from_user.id)

    items = message.text.split('&')
    answer = json.loads(items[1])
    if 'fund_id' in answer:
        fund_id = answer['fund_id']
        invite_url = answer['invite_url']
        await state.update_data(fund_id=fund_id)
        await state.update_data(invite_url=invite_url)

        keyboard = show_invite_link_keyboard()
        msg = f'Поздравляю, вы успешно создали сбор.\nСкопируйте эту ссылку и отправьте друзьям, ' \
              f'что бы пригласить их участвовать\n\nСсылка: {invite_url}'
        await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        await state.set_state(Steps.show_visitor_fund_link)
        return

    _msg = await message.answer("Не удалось зарегистрировать пробный сбор.")
    msgs.put(_msg)


async def query_show_main_menu(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await call.message.delete()
    user_data = await state.get_data()
    # все данные о пользователе
    exist_user_status = user_data['user_status']
    account_id = user_data['account_id']
    fund_id = user_data['fund_id']
    invite_url = user_data['invite_url']
    user_status = db.get_user_status(call.from_user.id, account_id=account_id, has_invite_url=False)
    await state.update_data(user_status=user_status)

    await start_trial_user(call.message, state)


async def query_show_invite_link_continue(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    # await call.message.delete()
    user_data = await state.get_data()
    # все данные о пользователе
    user_status = user_data['user_status']
    account_id = user_data['account_id']
    fund_id = user_data['fund_id']
    invite_url = user_data['invite_url']
    await fund_info(call.message, fund_id, state)


async def query_show_fund_link(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await call.message.delete()
    user_data = await state.get_data()
    invite_url = user_data.get('invite_url', None)

    keyboard = show_invite_link_keyboard()
    msg = f'Поздравляю, вы успешно создали сбор.\nСкопируйте эту ссылку и отправьте друзьям, ' \
          f'что бы пригласить их участвовать\n\nСсылка: {invite_url}'
    await call.message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(Steps.show_fund_link)
    return
    pass


async def query_return_menu(call: types.CallbackQuery, state: FSMContext) -> types.Message:
    await call.message.delete()
    user_id = call.from_user.id
    user_data: dict = await state.get_data()
    if 'user_status' in user_data and user_data['user_status'] == UserStatus.TrialUser:
        await start_trial_user(call.message, state)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_show_fund_link, lambda c: c.data == 'show_fund_link', state="*")
    dp.register_callback_query_handler(query_return_menu, lambda c: c.data == 'return_menu', state="*")

    # start_trial_user
    dp.register_callback_query_handler(query_trial_fund_info, lambda c: c.data == 'trial_fund_info', state="*")

    dp.register_message_handler(webapp_create_user_account, filters.Text(startswith='webapp'),
                                state=Steps.reg_visitor)
    dp.register_message_handler(webapp_create_user_fund, filters.Text(startswith='webapp'),
                                state=Steps.create_fund)
    dp.register_callback_query_handler(query_show_invite_link_continue, lambda c: c.data == 'show_invite_link_continue',
                                       state=Steps.show_fund_link)
    dp.register_callback_query_handler(query_show_main_menu, lambda c: c.data == 'show_invite_link_continue',
                                       state=Steps.show_visitor_fund_link)
