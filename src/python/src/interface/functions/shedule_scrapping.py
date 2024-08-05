import datetime
import pytz
from main import bot
from interface.data.config import logs

from commands.crawler_runner import run_crawler
async def send_greeting():
    run_crawler()

    kyiv_tz = pytz.timezone('Europe/Kyiv')
    kyiv_time = datetime.datetime.now(kyiv_tz)
    await bot.send_message(logs, f'Привіт! Запуск спайдеру о {kyiv_time.strftime("%H:%M:%S")}')
