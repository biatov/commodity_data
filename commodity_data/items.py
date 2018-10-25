# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommodityDataItem(scrapy.Item):
    series_id = scrapy.Field()
    series_title = scrapy.Field()
    group = scrapy.Field()
    item = scrapy.Field()
    base_date = scrapy.Field()
    year = scrapy.Field()
    period = scrapy.Field()
    value = scrapy.Field()
