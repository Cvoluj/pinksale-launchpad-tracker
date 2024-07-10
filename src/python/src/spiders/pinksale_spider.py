import json
import re
import scrapy
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError

from rmq.utils.import_full_name import get_import_full_name
from items import ProjectItem
from pipelines import ProjectToDatabasePipeline

class Pinksalespider(scrapy.Spider):
    BASE_URL = 'https://www.pinksale.finance/'
    
    name = 'pinksale'
    start_urls = ['https://api.pinksale.finance/api/v1/pool/list?page=1&limit=21&excludeChainIds[]=97&excludeChainIds[]=501423']
    
    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
        'DNS_TIMEOUT': 10,
    }
    
    chain_id_map = {
        1: 'launchpad/ethereum/',
        25: 'launchpad/cronos/',
        56: 'launchpad/bsc/',
        137: 'launchpad/polygon/',
        250: 'launchpad/fantom/',
        369: 'launchpad/pulsechain/',
        1116: 'launchpad/core/',
        3797: 'launchpad/alvey/',
        7171: 'launchpad/bitrock/',
        8453: 'launchpad/base/',
        42161: 'launchpad/arbitrum/',
        43114: 'launchpad/avalanche/',
        501424: 'solana/launchpad/',
    }
    
    
    def start_requests(self):
        base_url = 'https://api.pinksale.finance/api/v1/pool/list'
        filters = ['upcoming', 'inprogress']
        
        for filter_type in filters:
            url = f"{base_url}?page=1&limit=21&filterBy={filter_type}&excludeChainIds[]=97&excludeChainIds[]=501423"
            yield scrapy.Request(url=url, callback=self.parse, meta={'filter': filter_type, 'page': 1})
    
    def parse(self, response: Response):
        filter_type = response.meta['filter']
        data = json.loads(response.body)
        projects = data.get('docs', [])
        for project in projects:
            item = ProjectItem()
            item['project_id'] = project['pool']['address']
            item['url'] = self.BASE_URL + self.chain_id_map.get(project['chainId'], 'NOTFOUND') + item['project_id']
            item['title'] = project['token']['name']
            item['platform'] = 'www.pinksale.finance'
            yield scrapy.Request(url=item['url'], callback=self.parse_detail, meta={'item': item})
                 
        
        next_page = data.get('nextPage')
        if next_page:
            next_url = response.url.split('?')[0] + f"?page={next_page}&limit=21&filterBy={filter_type}&excludeChainIds[]=97&excludeChainIds[]=501423"
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'filter': filter_type, 'page': next_page})
            
    def parse_detail(self, response: Response):
        item = response.meta['item']
        contacts = response.xpath('//div[@class="flex items-center gap-2.5 text-gray-500 mt-2 justify-center"]/a/@href').getall()
        item['website'] = None
        if contacts:
            item['website'] = contacts[0] if 't.me' not in contacts[0] else None
            item['telegram'] = next((url for url in contacts if 't.me' in url), None)
            item['twitter'] = next((url for url in contacts if 'x.com' in url), None)
            
        if item['website']:
            yield scrapy.Request(url=item['website'], callback=self.parse_website,  meta={'item': item}, errback=self.errback_httpbin)
        
    def parse_website(self, response: Response):
        item = response.meta['item']        
        email_pattern = re.compile(r'[\w\.-]+@[\w]+[\.][\w]+')
        emails = email_pattern.findall(response.body.decode('utf-8'))
        item['email'] = None
        
        if emails:
            item['email'] = emails[0] 
        
        yield item
        
    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            self.logger.error(failure.getErrorMessage())
        else:
            self.logger.error(repr(failure))
