from main import bot, dp
from aiogram import types
from keyboards.keyboards import get_start_keyboard
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from interface.data.config import logs
from interface.filters.filter import *
from interface.functions.shedule_scrapping import send_greeting


html = 'HTML'

# Define the scheduler
scheduler = AsyncIOScheduler(timezone='Europe/Kyiv')
async def scheduler_jobs():
    scheduler.add_job(send_greeting, 'cron', hour=17, minute=27)
    scheduler.start()

async def antiflood(*args, **kwargs):
    m = args[0]
    await m.answer("Не поспішай :)")

async def on_startup(dp):
    await scheduler_jobs()
    me = await bot.get_me()
    await bot.send_message(logs, f"Бот @{me.username} запущений!")

async def on_shutdown(dp):
    await bot.close()
    me = await bot.get_me()
    await bot.send_message(logs, f'Bot: @{me.username} зупинений!')

@dp.message_handler(IsPrivate(), commands=["start"])
@dp.throttled(antiflood, rate=1)
async def start(message: types.Message):
    user = message.from_user
    keyboard = get_start_keyboard()
    await message.answer(f"Привіт, {user.username}! \nВиберіть за який період бажаєте отримати звіт.", reply_markup=keyboard)