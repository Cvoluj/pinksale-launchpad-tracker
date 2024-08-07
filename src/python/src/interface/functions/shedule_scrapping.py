import os
import glob
import pytz
import datetime
from main import bot
from interface.data.config import logs


from commands.crawler_runner import run_crawler
async def send_report():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    kyiv_time = datetime.datetime.now(kyiv_tz)
    await bot.send_message(logs, f'Привіт! Запуск спайдеру о {kyiv_time.strftime("%H:%M:%S")}')
    run_crawler()

    await send_latest_exported_file()

async def send_latest_exported_file():
    EXPORT_PATH = r'../../storage/export/'
    files = sorted(glob.glob(os.path.join(EXPORT_PATH, '*.csv')), key=os.path.getmtime, reverse=True)
    
    if files:
        latest_file = files[0]
        with open(latest_file, 'rb') as file:
            await bot.send_document(logs, file, caption="Експортований CSV файл.")
    else:
        await bot.send_message(logs, "Не знайдено жодного експортованого файлу.")
