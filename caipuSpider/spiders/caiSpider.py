import scrapy

from caipuSpider import pipelines
from caipuSpider.items import CaiContentItem

index = 0


class CaiSpider(scrapy.Spider):
    name = 'caispider'

    # TODO 动态的从数据库中遍历所有类型，根据类型来查询所有菜详情
    start_urls = [
        "https://www.xiangha.com/caipu/z-jiachangcai/",
    ]

    pipeline = set([
        pipelines.CaiDetailPipeline,
    ])

    def parse(self, response):
        list = response.xpath('//div[@class="s_list"]/ul/li')
        for li in list:
            item = CaiContentItem()
            name = li.xpath('./a/@title').extract()[0]
            href = li.xpath('./a/@href').extract()[0]
            img = li.xpath('./a/img/@src').extract()[0]
            item['img'] = img
            item['name'] = name
            item['href'] = href
            yield scrapy.Request(url=item['href'], meta={'item': item},
                                 callback=self.pare_detail, dont_filter=True)

        nextPage = response.xpath('//a[@class="nextpage"]/@href').extract()[0]
        if nextPage is not None:
            # 只爬取五页数据
            if nextPage != "https://www.xiangha.com/caipu/z-jiachangcai/hot-5/":
                yield scrapy.Request(nextPage, callback=self.parse)
                self.log("下一页：：：：：" + nextPage)


    def pare_detail(self, response):
        item = response.meta['item']
        # 获取点击量和收藏量
        viewsandcollect = response \
            .xpath("//div[contains(@class, 'rec_social')]/div[@class='info']")
        views = viewsandcollect.xpath('./text()').extract()[0]
        views = views.replace(' ', '')
        views = views[0:len(views) - 2]
        collect = viewsandcollect.xpath('./span/span/text()').extract()[0]
        item['views'] = views
        item['collect'] = collect

        # 简介和提示
        item['brief'] = "暂无简介"
        item['tips'] = "暂无小提示"
        # 获取食材
        burden = response.xpath("//div[@class='cell']")
        burdens = ""
        for it in burden:
            burdenname = it.xpath('./text()').extract()
            burdenNumbs = it.xpath('.//span/text()').extract()
            if len(burdenname) == 0:
                name = it.xpath('./a/text()').extract()[0]
                burdenname.append(name)
            burdenname = burdenname[0].replace(' ', "")
            burdenNumbs = burdenNumbs[0].replace(' ', "")
            burdens += burdenname + ":" + burdenNumbs + ";"
        item['burden'] = burdens

        # 获取步骤
        makes = response.xpath("//ul[@id='CookbookMake']/li")
        steps = ""
        for make in makes:
            tep = make.xpath("./p/text()").extract()[0]
            imgurl = make.xpath('./img/@data-src').extract()[0]
            steps += tep + "&&" + imgurl + "||"
        item['makes'] = steps
        yield item
