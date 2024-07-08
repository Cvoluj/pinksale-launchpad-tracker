import scrapy
from scrapy.http import Response


class Pinksalespider(scrapy.Spider):
    name = 'pinksale'
    allowed_domains = ['pinksale.finance']
    start_urls = ['https://api.pinksale.finance/api/v1/pool/list?page=1&limit=21&excludeChainIds[]=97&excludeChainIds[]=501423/', 'https://www.pinksale.finance/launchpads']
    
    def start_request(self, response: Response):
        for url in self.start_urls:
            yield scrapy.Request(url)
            
    def parse(self, response: Response):
        print(response.body)