import json
import scrapy
from scrapy.http import Response
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
        }
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
            item['domain'] = 'www.pinksale.finance'
            item['project_id'] = project['pool']['address']
            item['url'] = self.BASE_URL + self.chain_id_map.get(project['chainId'], 'NOTFOUND') + item['project_id']
            item['title'] = project['token']['name']
            item['platform'] = 'TODO'
            yield scrapy.Request(url=item['url'], callback=self.parse_detail, meta={'item': item})
                 
        
        next_page = data.get('nextPage')
        if next_page:
            next_url = response.url.split('?')[0] + f"?page={next_page}&limit=21&filterBy={filter_type}&excludeChainIds[]=97&excludeChainIds[]=501423"
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'filter': filter_type, 'page': next_page})
            
    def parse_detail(self, response: Response):
        item = response.meta['item']
        item['contact'] = json.dumps(response.xpath('//div[@class="flex items-center gap-2.5 text-gray-500 mt-2 justify-center"]/a/@href').getall())
        yield item