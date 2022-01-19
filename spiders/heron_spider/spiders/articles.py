from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from heron_spider.items import HeronSpiderItem

import pandas as pd


class ArticleSpider(CrawlSpider):

    name = 'articles'
    allowed_domains = ['wikipedia.org']
    start_urls = set(map(lambda x: "https://en.wikipedia.org" + x,
                     pd.read_csv("../../crawlers/companyTickers.csv")['Link']))
    rules = [Rule(LinkExtractor(allow='(/wiki/)((?!:).)*$'),
                  callback='parse_items', follow=True), ]
    custom_settings = {
        "DEPTH_LIMIT": 1
    }

    def parse_items(self, response):
        article = HeronSpiderItem()
        article['parent'] = response.request.headers['referer']
        article['url'] = response.url
        article['depth'] = response.meta['depth']
        article['title'] = response.css('h1::text').extract_first()
        lastUpdated = response.css(
            'li#footer-info-lastmod::text').extract_first()
        article['lastUpdated'] = lastUpdated.replace(
            'This page was last edited on ', '')
        return article
