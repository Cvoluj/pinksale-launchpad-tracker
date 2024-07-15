import datetime
import pytz
from main import bot, dp
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from interface.data.config import logs

async def send_greeting():
    process = CrawlerProcess(get_project_settings())
    process.crawl('pinksale')
    process.start()

    kyiv_tz = pytz.timezone('Europe/Kyiv')
    kyiv_time = datetime.datetime.now(kyiv_tz)
    await bot.send_message(logs, f'Привіт! Запуск спайдеру о {kyiv_time.strftime("%H:%M:%S")}')
