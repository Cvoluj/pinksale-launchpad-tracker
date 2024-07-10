from scrapy import Field
from rmq.items import RMQItem


class ProjectItem(RMQItem):    
    project_id = Field()
    url = Field()
    platform = Field()
    email = Field()
    title = Field()
    website = Field()
    telegram = Field()
    twitter = Field()