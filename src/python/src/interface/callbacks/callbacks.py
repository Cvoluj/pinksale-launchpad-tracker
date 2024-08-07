import glob
import os
from aiogram import types
from aiogram.dispatcher import Dispatcher

EXPORT_PATH = r'../../storage/export/'

def get_latest_files(n):
    files = sorted(glob.glob(os.path.join(EXPORT_PATH, '*.csv')), key=os.path.getmtime, reverse=True)
    return files[:n]

async def send_latest_file(callback_query: types.CallbackQuery):
    files = get_latest_files(1)
    if files:
        await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(files[0]))
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()

async def send_latest_three_files(callback_query: types.CallbackQuery):
    files = get_latest_files(3)
    if files:
        for file in files:
            await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(file))
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()

async def send_latest_seven_files(callback_query: types.CallbackQuery):
    files = get_latest_files(7)
    if files:
        for file in files:
            await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(file))
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(send_latest_file, lambda c: c.data == 'action1')
    dp.register_callback_query_handler(send_latest_three_files, lambda c: c.data == 'action2')
    dp.register_callback_query_handler(send_latest_seven_files, lambda c: c.data == 'action3')
