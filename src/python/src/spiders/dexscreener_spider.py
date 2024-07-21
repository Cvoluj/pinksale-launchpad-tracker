import scrapy
from scrapy.http import TextResponse
from scrapy.utils.reactor import install_reactor
import asyncio
import nodriver as uc

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

class DexScreenerSpider(scrapy.Spider):
    
    name = 'dexscreener'
    start_urls = ['https://dexscreener.com/page-1?rankBy=trendingScoreH24&order=desc']
    BASE_URL = 'https://dexscreener.com/'
    page_number = 1
    
    def __init__(self, *args, **kwargs):
        super(DexScreenerSpider, self).__init__(*args, **kwargs)
        self.loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(self.loop)
    
    def start_requests(self):
        for url in self.start_urls:
            content = self.loop.run_until_complete(self.fetch_content(url))
            response = scrapy.http.TextResponse(url=url, body=content, encoding='utf-8')
            yield from self.parse_pagination(response)

    def parse_pagination(self, response: TextResponse):
        urls = [self.BASE_URL + href for href in response.xpath('//*[@id="root"]/div/main/div/div[4]/a/@href').getall()]
        print(urls)
        print(response.xpath('//*[@id="root"]/div/main/div/div[4]/a/div[1]').getall())
        
        self.page_number += 1
        next_page = f'https://dexscreener.com/page-{self.page_number}?rankBy=trendingScoreH24&order=desc'
        
        if response.status == 200:
            content = self.loop.run_until_complete(self.fetch_content(next_page))
            next_response = scrapy.http.TextResponse(url=next_page, body=content, encoding='utf-8')
            yield from self.parse_pagination(next_response)
            
    async def fetch_content(self, url):
        browser = await uc.start()
        page = await browser.get(url)
        result = await page.select('#root > div > main > div > div.ds-dex-table.ds-dex-table-top > div > div.ds-table-th.ds-dex-table-th-token > button')
        content = await page.get_content()
        
        if not result:
            try:
                checkbox = await page.select('#Uiuv1 > div > label > input[type=checkbox]')
                await checkbox.click()
                self.logger.info('Cloudflare bypassed with checkbox')
            except Exception:
                self.logger.info('Cloudflare bypassed without checkbox')
                
        browser.stop()
        return content