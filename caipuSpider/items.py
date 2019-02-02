# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CaipuspiderItem(scrapy.Item):
    name = scrapy.Field()
    childItems = scrapy.Field()  # 子孩子
    level = scrapy.Field()  # 当前级别
    leibie = scrapy.Field()  # 类别方式 ：1 分类 2 食材
