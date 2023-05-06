import asyncio
import logging

from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from dotenv import load_dotenv, dotenv_values

from handlers.common import register_handlers_common
from handlers.company import register_handlers_company
from handlers.new import register_handlers_new
from handlers.private import register_handlers_private
from handlers.referal import register_handlers_referal


def load_config(env_path: str) -> dict:
    load_dotenv()
    config = dotenv_values(env_path)
    return config


async def webapp_answer(message: types.Message):
    await message.answer(message.web_app_data.data)
    await message.answer('Красивенько 😍')


async def cmd_delete_msg(message: types.Message):
    await message.delete()


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', )

    # Парсинг файла конфигурации
    config = load_config(".env")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=config['TOKEN'])
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_new(dp)
    register_handlers_company(dp)
    register_handlers_private(dp)
    register_handlers_referal(dp)
    dp.register_message_handler(webapp_answer, content_types=[ContentType.WEB_APP_DATA])
    dp.register_message_handler(cmd_delete_msg)

    # Запуск
    await dp.start_polling()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    asyncio.run(main())
