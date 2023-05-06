from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BotConfig

bot_config = BotConfig.instance()


def create_user(user, query_id: str, user_id):
    print(user)
    pass


def create_new_keyboard():
    url1 = f'{bot_config.base_url}content/userRegistration'
    url2 = f'{bot_config.base_url}/webapp/templates/index'
    url3 = f'{bot_config.base_url}/webapp/templates/bot'
    buttons = [
        InlineKeyboardButton(text="Регистрация для друзей", web_app=types.WebAppInfo(url=url1)),
        InlineKeyboardButton(text="Регистрация компании",  web_app=types.WebAppInfo(url=url2)),
        InlineKeyboardButton(text="Демо",  web_app=types.WebAppInfo(url=url3)),
        InlineKeyboardButton(text="В начало", callback_data='home'),
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


async def query_new_user(call: types.CallbackQuery):
    keyboard = create_new_keyboard()
    msg = 'Вы можете зарегистрироваться только для одного сбора или ' \
          'сразу зарегистрировать вашу компанию, если планируете и ' \
          'дальше использовать Дружбу.'
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()


def register_handlers_new(dp: Dispatcher):
    # dp.register_message_handler(cmd_new_user, commands="new_user", state="*")
    dp.register_callback_query_handler(query_new_user, lambda c: c.data == 'new_user', state="*")
    # dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    # dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    pass
