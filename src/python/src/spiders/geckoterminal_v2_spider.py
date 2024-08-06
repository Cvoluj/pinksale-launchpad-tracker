import json
import re
import scrapy
from scrapy import signals
from datetime import datetime, timedelta
from twisted.internet.error import DNSLookupError
from scrapy.http import Response, JsonRequest, Request
from scrapy.spidermiddlewares.httperror import HttpError
from rmq.utils.import_full_name import get_import_full_name
from pipelines import ProjectToDatabasePipeline

from items import ProjectItem

class GeckoTerminalV2Spider(scrapy.Spider):
    name = 'gecko_v2'
    BASE_URL = 'https://www.geckoterminal.com/'
    PAGINATION_URL = 'https://api.geckoterminal.com/api/v2/networks/new_pools'

    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
    }
    
    start_urls = [
        'data:,'
    ]

    # use for setting up how old pools to scrap
    hours = 12

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GeckoTerminalV2Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_time = datetime.now()
        self.time_difference = timedelta()

    def parse(self, response: Response):
        page = 1
        yield JsonRequest(f'{self.PAGINATION_URL}?page={page}',
                            callback=self.parse_pagination, meta={
                                'page': page,
                            })
        
    def parse_pagination(self, response: Response):
        page = response.meta.get('page')
        data = json.loads(response.body)

        for crypto_pool in data['data']:
            item = ProjectItem()
            item['project_id'] = crypto_pool['id']
            item['url'] = f"{self.BASE_URL}{item['project_id'].replace('_', '/pools/')}"
            item['platform'] = 'www.geckoterminal.com'
            item['title'] = crypto_pool['attributes']['name']

            time = datetime.strptime(crypto_pool['attributes']['pool_created_at'], "%Y-%m-%dT%H:%M:%SZ")
            self.time_difference = self.current_time - time

            yield Request(item['url'], callback=self.parse_detail_page, meta={'item': item})

        if data['data'] and self.time_difference <= timedelta(hours=self.hours):
            page += 1
            yield JsonRequest(
                f'{self.PAGINATION_URL}?page={page}',
                callback=self.parse_pagination,
                meta={'page': page,},
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

    def form_chains(self, data, chains = {}):
        networks = {network['id']: network['attributes'].get('identifier') for network in data['included'] if network['type'] == 'network'}        
        for chain in data['data']:
            main_chain_id = chain['relationships'].get('network').get('data').get('id')
            if main_chain_id:
                chains[chain['id']] = networks[main_chain_id]
          
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
