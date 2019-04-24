import functools

import scrapy

from caipuSpider import pipelines
from caipuSpider.items import CaipuspiderItem as Item


class xianghaSpider(scrapy.Spider):
    name = 'xianghaspider'
    start_urls = [
        "https://www.xiangha.com/caipu/",
        # "https://www.xiangha.com/jiankang/"
    ]
    pipeline = set([
        pipelines.CaipuspiderPipeline,
    ])

    def parse(self, response):
        contain = response.xpath("//div[contains(@class, 'rec_classify_cell')]")

        parent = contain.xpath('./h3')
        for item in parent:
            # 获取当前节点的文字内容
            parentName = item.xpath('./text()')[0].extract()
            parentItem = Item()
            parentItem['name'] = parentName
            parentItem['level'] = 1
            parentItem['leibie'] = '1'

            # 获取当前节点的下一个节点元素
            childList = item.xpath('./following-sibling::*[1]/li/a')
            dic = []
            for child in childList:
                childName = child.xpath('./text()')[0].extract()
                url = child.xpath('./@href').extract()[0]
                item = Item()
                item['name'] = childName
                item['level'] = 2
                item['url'] = url
                item['leibie'] = '1'
                dic.append(item)

            parentItem['childItems'] = dic
            yield parentItem

