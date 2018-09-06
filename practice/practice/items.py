# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PracticeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EloquiiItem(scrapy.Item):
    name = scrapy.Field()
    availability = scrapy.Field()
    ID = scrapy.Field()
    weblink = scrapy.Field()
    image = scrapy.Field()
