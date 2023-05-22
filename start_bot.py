import asyncio
import logging

from bot.start_bot import start

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    asyncio.run(start())
