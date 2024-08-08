import glob
import os
import csv
from aiogram import types
from aiogram.dispatcher import Dispatcher

from interface.data.config import EXPORT_PATH

def get_latest_files(n):
    files = sorted(glob.glob(os.path.join(EXPORT_PATH, '*.csv')), key=os.path.getmtime, reverse=True)
    return files[:n]

def merge_csv_files(file_list, output_path):
    with open(file_list[0], 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

    with open(output_path, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        for file in file_list:
            with open(file, 'r', encoding='utf-8') as f_in:
                reader = csv.reader(f_in)
                next(reader) 
                for row in reader:
                    writer.writerow(row)

async def send_1_days_report(callback_query: types.CallbackQuery):
    files = get_latest_files(2)
    if files:
        output_path = os.path.join(EXPORT_PATH, 'report_1.csv')
        merge_csv_files(files, output_path)
        await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(output_path), caption="1 day report")
        os.remove(output_path)
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()

async def send_3_days_report(callback_query: types.CallbackQuery):
    files = get_latest_files(6)
    if files:
        output_path = os.path.join(EXPORT_PATH, 'report_3.csv')
        merge_csv_files(files, output_path)
        await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(output_path), caption="3 days report")
        os.remove(output_path)
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()
    
async def send_7_days_report(callback_query: types.CallbackQuery):
    files = get_latest_files(14)
    if files:
        output_path = os.path.join(EXPORT_PATH, 'report_7.csv')
        merge_csv_files(files, output_path)
        await callback_query.bot.send_document(callback_query.from_user.id, types.InputFile(output_path), caption="7 days report")
        os.remove(output_path)
    else:
        await callback_query.bot.send_message(callback_query.from_user.id, "No files found.")
    await callback_query.answer()



def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(send_1_days_report, lambda c: c.data == 'action1')
    dp.register_callback_query_handler(send_3_days_report, lambda c: c.data == 'action2')
    dp.register_callback_query_handler(send_7_days_report, lambda c: c.data == 'action3')
