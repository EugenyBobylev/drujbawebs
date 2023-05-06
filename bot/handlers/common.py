from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from config import BotConfig
from db.bl import get_session, get_msg

bot_config = BotConfig.instance()


def create_start_keyboard():
    buttons = [
        InlineKeyboardButton(text="Новый", callback_data='new_user'),
        InlineKeyboardButton(text="Приват", callback_data='private_user'),
        InlineKeyboardButton(text="Компания", callback_data="company_user")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def create_app_keyboard():
    url1 = f'{bot_config.base_url}content/userRegistration'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    buttons = [
        types.KeyboardButton(text='Новый', web_app=types.WebAppInfo(url=url1)),
        types.KeyboardButton(text='Старый', web_app=types.WebAppInfo(url=url2)),
    ]
    keyboard = types.ReplyKeyboardMarkup()
    for btn in buttons:
        keyboard.add(btn)
    return keyboard


async def cmd_start(message: types.Message):
    session = get_session()
    msg = get_msg('start_message', session).text_value.replace("\\n", "\n")
    keyboard = create_start_keyboard()
    # keyboard = create_app_keyboard()
    await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await message.delete()


async def query_start(call: types.CallbackQuery):
    await cmd_start(call.message)


async def query_new_user(call: types.CallbackQuery):
    # await cmd_new_user(call.message)
    await call.message.delete()
    # await call.answer('переход к действиям нового пользователя', c)


async def query_private_user(call: types.CallbackQuery):
    await call.answer('переход к действиям частного пользователя')


async def query_company_user(call: types.CallbackQuery):
    await call.answer('переход к действиям корпоративного пользователя')


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(query_start, lambda c: c.data == 'home', state="*")
    dp.register_callback_query_handler(query_private_user, lambda c: c.data == 'private_user', state="*")
    dp.register_callback_query_handler(query_company_user, lambda c: c.data == 'company_user', state="*")
