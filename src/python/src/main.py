import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from interface.data.config import token
from interface.callbacks.callbacks import register_callbacks

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Bot and Dispatcher setup
bot = Bot(token=token, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler(timezone='Europe/Kyiv')

register_callbacks(dp)

if __name__ == '__main__':
    from interface.handlers.handlers import dp, on_startup, on_shutdown
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
