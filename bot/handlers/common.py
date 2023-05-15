import json
from queue import Queue

from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

import db
from config import BotConfig
from db.bl import get_session, get_msg

bot_config = BotConfig.instance()

msgs = Queue()  #


def start_registered_user(message: types.Message):
    pass


async def start_new_user(message: types.Message):
    session = get_session()
    msg = get_msg('start_message', session).text_value.replace("\\n", "\n")

    keyboard = new_user_start_keyboard()
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    msgs.put(_msg)


async def start_trial_user(message):
    session = get_session()
    user_id = message.from_user.id
    user = db.get_user(user_id, session)
    name = user.name
    msg = get_msg('trial_menu', session).text_value.replace("\\n", "\n").format(name=name)
    keyboard = trial_user_start_keyboard()
    _msg = await message.answer(msg, parse_mode=ParseMode.HTML)
    msgs.put(_msg)


def new_user_start_keyboard():
    url1 = f'{bot_config.base_url}UserRegistration'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    buttons = [
        InlineKeyboardButton(text="Организовать сбор на подарок", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Зарегистрировать компанию", web_app=types.WebAppInfo(url=url2)),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def trial_user_start_keyboard():
    url1 = f'{bot_config.base_url}UserRegistration'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    buttons = [
        InlineKeyboardButton(text="Организовать сбор на подарок", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Зарегистрировать компанию", web_app=types.WebAppInfo(url=url2)),
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


async def cmd_start(message: types.Message):
    await message.delete()
    session = get_session()

    user_id = message.from_user.id
    is_registered: bool = db.is_user_registered(user_id, session)
    companies = db.get_user_companies(user_id, session)
    if not is_registered:   # пользователь не зарегистрирован
        await start_new_user(message)
        return

    # обычный пользователь
    if len(companies) == 0:
        account = db.get_user_account(user_id, session)
        funds = db.get_all_fundraisings(account.id, session)
        if len(funds) == 1:
            # в меню управления бесплатным сбором
            await start_trial_user(message)
        if len(funds) > 0:
            # в меню ЛК пользователя
            pass
        return

    # админ компании
    if len(companies) > 0:
        company = companies[0]
        # в меню ЛЛ админа компании
        pass


async def query_start(call: types.CallbackQuery):
    await cmd_start(call.message)


async def query_new_user(call: types.CallbackQuery):
    # await cmd_new_user(call.message)
    await call.message.delete()
    # await call.answer('переход к действиям нового пользователя', c)


async def query_new_fundraising(call: types.CallbackQuery):
    await call.answer('переход к действиям частного пользователя')


async def query_register_company(call: types.CallbackQuery):
    await call.answer('Зарегистрировать компанию!')


async def webapp_answer_msg(message: types.Message):
    await message.delete()
    items = message.text.split('&')
    operation = items[1]
    data = json.loads(items[2])
    if operation == 'UserRegistration':
        while not msgs.empty():
            m = msgs.get()
            if type(m) == types.Message:
                await m.delete()

        session = get_session()
        user_id = message.from_user.id
        ok = db.is_user_registered(user_id, session)
        if ok:
            account = db.get_user_account(user_id, session)
            if account is None or account.payed_events < 1:
                await message.answer('Вы не можете создать сбор, так как у вас нет оплаченных сборов.')
                return

        keyboard = new_private_fund_keyboard()
        msg = 'Вы успешно зарегистрировались. Давайте продолжим.'
        _msg = await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        msgs.put(_msg)

    if operation == 'CreatePrivateFundraising':
        while not msgs.empty():
            m = msgs.get()
            if type(m) == types.Message:
                await m.delete()
        session = get_session()
        if 'fundrasing_id' in data and data['fundrasing_id']:
            user_id = message.from_user.id
            account = db.get_user_account(user_id, session)
            account.payed_events -= 1
            session.commit()
        msg = f'Поздравляю, вы успешно создали сбор.\nСкопируйте эту ссылку и отправьте друзьям, ' \
              f'что бы пригласить их участвовать\n\nСсылка: {data["invite_url"]}'
        await message.answer(msg)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_new_fundraising, lambda c: c.data == 'new_fundraising', state="*")
    dp.register_callback_query_handler(query_register_company, lambda c: c.data == 'register_company', state="*")
    dp.register_message_handler(webapp_answer_msg, filters.Text(startswith='webapp'))

