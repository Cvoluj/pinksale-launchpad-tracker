from main import bot, dp
from interface.data.config import logs
from interface.filters.filter import *
from interface.functions.shedule_scrapping import send_greeting
from keyboards.keyboards import get_start_keyboard

import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, KeyboardButton, ContentTypes, ReplyKeyboardMarkup, \
    InputFile

from apscheduler.schedulers.asyncio import AsyncIOScheduler


html = 'HTML'

# Define the scheduler
scheduler = AsyncIOScheduler(timezone='Europe/Kyiv')
async def scheduler_jobs():
    scheduler.add_job(send_greeting, 'cron', hour=14, minute=52)
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