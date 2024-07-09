from scrapy import Field
from rmq.items import RMQItem


class ProjectItem(RMQItem):    
    project_id = Field()
    url = Field()
    domain = Field()
    platform = Field()
    title = Field()
    website = Field()
    contact = Field()