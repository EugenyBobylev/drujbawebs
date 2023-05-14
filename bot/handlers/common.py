from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

import db
from config import BotConfig
from db.bl import get_session, get_msg

bot_config = BotConfig.instance()


def start_registered_user(message: types.Message):
    pass


async def start_new_user(message: types.Message):
    session = get_session()
    msg = get_msg('start_message', session).text_value.replace("\\n", "\n")

    keyboard = new_user_start_keyboard()
    await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


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
    session = get_session()

    user_id = message.from_user.id
    is_registered: bool = db.is_user_registered(user_id, session)
    if is_registered:    # go to main menu
        start_registered_user(message)
    await start_new_user(message)
    await message.delete()


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


async def user_registration_msg(message: types.Message):
    await message.delete()
    items = message.text.split('=')
    if len(items) == 2:
        user_id = items[1]
        keyboard = new_private_fund_keyboard()
        msg = 'Вы успешно зарегистрировались. Давайте продолжим.'
        await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_new_fundraising, lambda c: c.data == 'new_fundraising', state="*")
    dp.register_callback_query_handler(query_register_company, lambda c: c.data == 'register_company', state="*")
    dp.register_message_handler(user_registration_msg, filters.Text(startswith='webapp UserRegistration'))

