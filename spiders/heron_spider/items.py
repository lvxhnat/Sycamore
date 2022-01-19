# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HeronSpiderItem(scrapy.Item):
    url = scrapy.Field()
    parent = scrapy.Field()
    title = scrapy.Field()
    depth = scrapy.Field()
    lastUpdated = scrapy.Field()
