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


class CaiContentItem(scrapy.Item):
    name = scrapy.Field()  # 姓名
    brief = scrapy.Field()  # 简介
    tips = scrapy.Field()  # 提示
    views = scrapy.Field()  # 浏览量
    collect = scrapy.Field()  # 收藏量
    makes = scrapy.Field()  # 步骤
    burden = scrapy.Field()  # 用料
    img = scrapy.Field()  # 封面图
    href = scrapy.Field()  #详情地址
