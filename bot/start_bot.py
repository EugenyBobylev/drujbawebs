import asyncio
import logging

from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BotConfig
from bot.handlers.common import register_handlers_common


async def cmd_delete_msg(message: types.Message):
    await message.delete()


async def start():
    # Настройка логирования в stdout
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', )

    # Объявление и инициализация объектов бота и диспетчера
    token = BotConfig.instance().token
    bot = Bot(token=token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    dp.register_message_handler(cmd_delete_msg, )

    # Запуск
    storage: MemoryStorage = MemoryStorage()
    await dp.start_polling(storage)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    asyncio.run(start())
