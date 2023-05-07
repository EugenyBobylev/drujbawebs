import asyncio
import logging

import aiohttp
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from dotenv import load_dotenv, dotenv_values

from config import BotConfig
from handlers.common import register_handlers_common
from handlers.company import register_handlers_company
from handlers.new import register_handlers_new
from handlers.private import register_handlers_private
from handlers.referal import register_handlers_referal


async def cmd_delete_msg(message: types.Message):
    await message.delete()


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', )

    # Объявление и инициализация объектов бота и диспетчера
    token = BotConfig.instance().token
    bot = Bot(token=token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_new(dp)
    register_handlers_company(dp)
    register_handlers_private(dp)
    register_handlers_referal(dp)
    dp.register_message_handler(cmd_delete_msg, )

    # Запуск
    await dp.start_polling()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    asyncio.run(main())
