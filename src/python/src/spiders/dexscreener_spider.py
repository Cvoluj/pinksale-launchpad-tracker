import re
import scrapy
import asyncio
import nodriver as uc
from scrapy.http import TextResponse, Response
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from MySQLdb.cursors import DictCursor
from twisted.enterprise.adbapi import ConnectionPool

from items import ProjectItem
from pipelines import ProjectToDatabasePipeline

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

class DexScreenerSpider(scrapy.Spider):
    name = 'dexscreener'
    project_settings = get_project_settings()
    
    start_urls = [
        'https://dexscreener.com/page-1?rankBy=pairAge&order=asc',
        
        # link for checking, because on trending we have more info and websites
        # 'https://dexscreener.com/?rankBy=trendingScoreH24&order=desc', 
        ]
    
    BASE_URL = 'https://dexscreener.com/'
    page_number = 1
    
    def __init__(self, *args, **kwargs):
        super(DexScreenerSpider, self).__init__(*args, **kwargs)
        self.pipeline = ProjectToDatabasePipeline(self.logger, self.project_settings)
        self.pipeline.conn = ConnectionPool(
                "MySQLdb",
                host=self.project_settings.get("DB_HOST"),
                port=self.project_settings.get("DB_PORT"),
                user=self.project_settings.get("DB_USERNAME"),
                passwd=str(self.project_settings.get("DB_PASSWORD")),
                db=self.project_settings.get("DB_DATABASE"),
                cursorclass=DictCursor,
                charset="utf8mb4",
                cp_reconnect=True,
            )
        self.loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(self.loop)
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request('data:,', callback=self.initial_parse_pagination, meta={'url': url})
    
    async def initial_parse_pagination(self, response):
        url = response.meta['url']
        content = self.loop.run_until_complete(self.fetch_pagination(url))
        response = scrapy.http.TextResponse(url=url, body=content, encoding='utf-8')
        await self.parse_pagination(response)

    async def parse_pagination(self, response: TextResponse):
        urls = [self.BASE_URL + href for href in response.xpath('//*[@id="root"]/div/main/div/div[4]/a/@href').getall()]
        titles = response.xpath('//*[@id="root"]/div/main/div/div[4]/a/div[1]/span[2]/text()').getall()
        for url, title in zip(urls, titles):
            item = ProjectItem()
            item['platform'] = 'dexscreener.com'
            item['url'] = url
            item['project_id'] = url.split('/')[-1]            
            item['title'] = title
            
            detail_page_content = self.loop.run_until_complete(self.fetch_detail_page(url))
            response = scrapy.http.TextResponse(url=url, body=detail_page_content, encoding='utf-8')
            await self.parse_detail_page(response, meta={"item": item})
            
        self.page_number += 1
        next_page = f'https://dexscreener.com/page-{self.page_number}?rankBy=trendingScoreH24&order=desc'
        
        if response.status == 200 and self.page_number <= self.project_settings.getint("DEXSCRENER_PAGE_COUNT"):
            content = self.loop.run_until_complete(self.fetch_pagination(next_page))
            next_response = scrapy.http.TextResponse(url=next_page, body=content, encoding='utf-8')
            await self.parse_pagination(next_response)
                        
    async def parse_detail_page(self, response: TextResponse, meta: dict):
        item = meta["item"]
        
        contacts = response.xpath('//*[@id="root"]/div/main/div/div/div[1]/div/div[1]/div[2]/div/div/a/@href').getall()
        self.logger.info(contacts)
        item['website'] = None
        if contacts:
            item['website'] = next((url for url in contacts if 't.me' not in url and 'x.com' not in url), None)
            item['telegram'] = next((url for url in contacts if 't.me' in url), None)
            item['twitter'] = next((url for url in contacts if 'x.com' in url), None)        
        if item['website']:
            self.logger.info(f'Found website: {item["website"]}')
            content = self.loop.run_until_complete(self.fetch_website(item['website']))
            next_response = scrapy.http.TextResponse(url=item['website'], body=content, encoding='utf-8')
            await self.parse_website(next_response, meta={'item': item})
        
    async def parse_website(self, response: Response, meta: dict):
        item = meta['item']
        self.logger.info(f'Parsing website for project {item["title"]}')
        email_pattern = re.compile(r'[\w\.-]+@[\w]+[\.][\w]+')
        emails = email_pattern.findall(response.body.decode('utf-8'))
        item['email'] = None
        if emails:
            item['email'] = emails[0]
            self.logger.info(f'Found email: {item["email"]}')
        self.pipeline.process_item(item=item, spider=self)
            
    async def fetch_pagination(self, url):
        browser = await uc.start()
        page = await browser.get(url)
        try:
            await page.select('#root > div > main > div > div.ds-dex-table.ds-dex-table-top > div > div.ds-table-th.ds-dex-table-th-token > button')
        except Exception:
            self.logger.warning(f"Could not resolve cloudflare for {url}")
        content = await page.get_content()
                
        browser.stop()
        return content
    
    async def fetch_detail_page(self, url):
        browser = await uc.start()
        page = await browser.get(url)
        try:
            await page.select('#root > div')
        except Exception:
            self.logger.warning(f"Could not resolve cloudflare for {url}")
        content = await page.get_content()
                
        browser.stop()
        return content
    
    async def fetch_website(self, url):
        browser = await uc.start()
        page = await browser.get(url)
        content = await page.get_content()
                
        browser.stop()
        return content

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            self.logger.error(failure.getErrorMessage())
        else:
            self.logger.error(repr(failure))
            