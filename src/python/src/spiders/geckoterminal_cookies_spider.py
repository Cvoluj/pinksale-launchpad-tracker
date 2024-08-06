import json
import re
from typing import Iterable
import scrapy
from scrapy import signals
from datetime import datetime, timedelta
from twisted.internet.error import DNSLookupError
from scrapy.http import Response, JsonRequest, Request
from scrapy.spidermiddlewares.httperror import HttpError
from rmq.utils.import_full_name import get_import_full_name
from pipelines import ProjectToDatabasePipeline

from items import ProjectItem

class GeckoTerminalSpider(scrapy.Spider):
    name = 'gecko_v1'
    cookie_string = '__cf_bm=Fhn.jOWk8T3CyKYXf1H.WydNjhXA20psq.Lwhp7P01M-1722986962-1.0.1.1-t6PqlNb.l7COZPwHErb2gt6q.yauAtqkTRnynkoqt9dqAXCArnZTiYLmUe5K3eYsEDkVuRzOTshpcEeiFdoHhw; Expires=Tue, 06 Aug 2024 23:59:22 GMT; Domain=geckoterminal.com; Path=/; Secure; HttpOnly'
    BASE_URL = 'https://www.geckoterminal.com/'
    PAGINATION_URL = 'https://app.geckoterminal.com/api/p1/latest_pools?pool_creation_hours_ago%5Blte%5D=72'

    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
    }
    
    start_urls = [
        'https://app.geckoterminal.com/api/p1/dexes?include=network%2Cdex_metric',
    ]

    # use for setting up how old pools to scrap
    hours = 12

    def start_requests(self):
        yield Request(self.start_urls[0], cookies=self.parse_cookies(self.cookie_string),
)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GeckoTerminalSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_time = datetime.now()
        self.time_difference = timedelta()

    def parse(self, response: Response):
        chains = {
            '17495': 'flare',
            '13174': 'solana',
            '3': 'polygon_pos',
        }
        data = json.loads(response.body)

        networks = {network['id']: network['attributes'].get('identifier') for network in data['included'] if network['type'] == 'network'}        
        for chain in data['data']:
           main_chain_id = chain['relationships'].get('network').get('data').get('id')
           if main_chain_id:
            chains[chain['id']] = networks[main_chain_id]
        
        page = 1
        yield JsonRequest(f'{self.PAGINATION_URL}?page={page}',
                            callback=self.parse_pagination, meta={
                                'chains': chains,
                                'page': page,
                            })
        
    def parse_pagination(self, response: Response):
        chains = response.meta.get('chains')
        page = response.meta.get('page')
        data = json.loads(response.body)

        for crypto_pool in data['data']:
            item = ProjectItem()
            id = crypto_pool.get('relationships').get('dex').get('data').get('id')
            network_id = chains.get(id)
            item['project_id'] = crypto_pool['attributes']['address']
            item['url'] = f"{self.BASE_URL}{network_id}/pools/{item['project_id']}"
            item['platform'] = 'www.geckoterminal.com'
            item['title'] = crypto_pool['attributes']['name']

            time = datetime.strptime(crypto_pool['attributes']['pool_created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            self.time_difference = self.current_time - time

            if network_id is None:
                self.logger.warning("Network id is None: %s %s %s", id, item["title"], item['url'])

            yield Request(item['url'], callback= self.parse_detail_page, meta={'item': item})

        if data['data'] and self.time_difference <= timedelta(hours=self.hours):
            print(self.time_difference)
            page += 1
            yield JsonRequest(
                f'{self.PAGINATION_URL}&page={page}',
                callback=self.parse_pagination,
                meta={'chains': chains, 'page': page},
                errback=self.errback_httpbin
            )
    
    def parse_detail_page(self, response: Response):
        item = response.meta['item']

        contacts = response.xpath('//*[@id="__next"]/div/main/div[2]/div[1]/div/div/div/div/div[2]/div[2]/div/div/a/@href').getall()
        self.logger.info("Find contacts: %s", contacts)
        item['website'] = None
        if contacts:
            item['website'] = next((url for url in contacts if 't.me' not in url and 'x.com' not in url), None)
            item['telegram'] = next((url for url in contacts if 't.me' in url), None)
            item['twitter'] = next((url for url in contacts if 'x.com' in url), None)        
        if item['website']:
            self.logger.info(f'Found website: {item["website"]}')
            yield scrapy.Request(url=item['website'], callback=self.parse_website, meta={'item': item}, errback=self.errback_httpbin)
        elif item.get('twitter'):
            yield item

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

    def parse_cookies(self, raw_cookies):
        cookies = {}
        for cookie in raw_cookies.split('; '):    
            try:
                key = cookie.split('=')[0]
                val = cookie.split('=')[1]
                cookies[key] = val
            except Exception:
                pass
        return cookies