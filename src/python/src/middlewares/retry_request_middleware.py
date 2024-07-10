from scrapy import Spider, Request
from scrapy.http import Response

class RetryRequestMiddleware:
    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        if response.status == 403:
            request.headers["Connection"] = "close"
            retry_times = request.meta.get("retry_times", 0) + 1
            max_retry_times = spider.settings.getint("RETRY_TIMES", 5)

            if retry_times <= max_retry_times:
                spider.logger.info(f"Retrying {request.url} due to 403, attempt {retry_times}")
                request = request.copy()
                request.meta["retry_times"] = retry_times
                return request
        return response