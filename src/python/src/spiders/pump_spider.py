import json
import re
import scrapy
from scrapy import signals
from datetime import datetime, timedelta
from twisted.internet.error import DNSLookupError
from scrapy.http import Response, Request
from scrapy.spidermiddlewares.httperror import HttpError
from rmq.utils.import_full_name import get_import_full_name
from pipelines import ProjectToDatabasePipeline

from items import ProjectItem

class PumpSpider(scrapy.Spider):
    name = 'pump'
    BASE_URL = 'pump.fun'
    hours = 12

    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
        'DNS_TIMEOUT': 10,
    }
    
    start_urls = [
        'https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=true'
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PumpSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_time = datetime.now()
        self.time_difference = timedelta()


    def parse(self, response: Response):
        data = json.loads(response.body)

        for coin in data:
            item = ProjectItem()

            item['project_id'] = coin.get('mint')
            item['url'] =  f"{self.BASE_URL}/{item.get('project_id')}"
            item['platform'] = self.BASE_URL
            item['title'] = coin.get('name')

            website = coin.get('website')
            item['website'] = None
            if website:
                if 'x.com' not in website and 't.me' not in website:
                    if not website.startswith('http://') and not website.startswith('https://'):
                        website = 'http://' + website
                    item['website'] = website

            item['telegram'] = coin.get('telegram')
            item['twitter'] = coin.get('twitter')

            timestamp = datetime.fromtimestamp(coin.get('created_timestamp') / 1000) 
            self.time_difference = self.current_time - timestamp

            if item['website']:
                self.logger.info(f'Found website: {item["website"]}')
                yield scrapy.Request(url=item['website'], callback=self.parse_website, meta={'item': item}, errback=self.errback_httpbin)
            elif item.get('twitter'):
                yield item
        
        if data and self.time_difference <= timedelta(hours=self.hours):
            offset = response.meta.get('offset', 0) + 50
            next_url = f'https://frontend-api.pump.fun/coins?offset={offset}&limit=50&sort=created_timestamp&order=DESC&includeNsfw=true'
            yield Request(next_url, callback=self.parse, errback=self.errback_httpbin, meta={'offset': offset})
    
    def parse_website(self, response: Response):
        item = response.meta['item']
        self.logger.info(f'Parsing website for project {item["title"]}')
        email_pattern = re.compile(r'[\w\.-]+@[\w]+[\.][\w]+')
        emails = email_pattern.findall(response.body.decode('utf-8'))
        item['email'] = None
        if emails:
            item['email'] = emails[0]
            self.logger.info(f'Found email: {item["email"]}')
        yield item

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            self.logger.error(failure.getErrorMessage())
        else:
            self.logger.error(repr(failure))

    def spider_closed(self, spider):
        self.logger.info("Spider %s closed", self.name)
