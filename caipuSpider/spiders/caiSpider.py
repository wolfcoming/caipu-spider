import pymysql
import scrapy
from scrapy import Request

from caipuSpider import pipelines
from caipuSpider.items import CaiContentItem


class CaiSpider(scrapy.Spider):

    def __init__(self, dbparams):
        self.connect = pymysql.connect(
            host=dbparams['host'],
            port=dbparams['port'],
            db=dbparams['db'],
            user=dbparams['user'],
            passwd=dbparams['passwd'],
            charset=dbparams['charset'],
            use_unicode=dbparams['use_unicode']
        )
        self.XH_PAGENUMBER = dbparams['XH_PAGENUMBER']
        # 创建一个句柄
        self.cursor = self.connect.cursor()

    @classmethod
    def from_crawler(cls, crawler):

        # 读取settings中的配置
        dbparams = dict(
            host=crawler.settings.get('MYSQL_HOST'),
            db=crawler.settings.get('MYSQL_DBNAME'),
            user=crawler.settings.get('MYSQL_USER'),
            passwd=crawler.settings.get('MYSQL_PASSWD'),
            port=crawler.settings.get('MYSQL_POR'),
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            use_unicode=False,
            XH_PAGENUMBER=crawler.settings.get('XH_PAGENUMBER')
        )
        return cls(dbparams)

    name = 'caispider'

    # 动态的从数据库中遍历所有类型，根据类型来查询所有菜详情
    def start_requests(self):
        # 获取数据库中数据
        sql = 'select extralurl from app_menucategory'
        self.cursor.execute(sql)
        self.connect.commit()
        result = self.cursor.fetchall()
        result = list(result)
        # result = result[0:3]
        for url in result:
            myurl = url[0]
            if myurl is None:
                myurl = "None"
            else:
                myurl = myurl.decode()
            if myurl is not None and myurl != "None":
                print("当前请求的是：" + myurl)
                self.count = 0
                print("开始count：" + str(self.count))
                yield Request(myurl, dont_filter=True)

    pipeline = set([
        pipelines.CaiDetailPipeline,
    ])

    def parse(self, response):
        list = response.xpath('//div[@class="s_list"]/ul/li')
        print("当前页 个数：" + str(len(list)))
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
        self.count = self.count + 1
        if nextPage is not None:
            # 只爬取XH_PAGENUMBER页数据
            if self.count <= self.XH_PAGENUMBER - 1:
                print("当前count：" + str(self.count))
                yield scrapy.Request(nextPage, callback=self.parse)
                print("下一页：：：：：" + nextPage)

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

            if len(burdenNumbs) == 0:
                burdenNumbs = "少许"
            else:
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
