# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import functools

import pymysql
from scrapy import log


# 指定对应的管道处理内容 需要在
def check_spider_pipeline(process_item_method):
    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            spider.log(msg % 'executing', level=log.DEBUG)
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.log(msg % 'skipping', level=log.DEBUG)
            return item

    return wrapper


class CaipuspiderPipeline(object):
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
        )
        return cls(dbparams)

    @check_spider_pipeline
    def process_item(self, item, spider):
        childs = item['childItems']
        name = item['name']
        brief = item['name']
        category_level = item['level']
        parent_category_id = None
        category_way = item['leibie']
        islast_level = False

        # # 将数据写入数据库
        if spider.name != None:

            # 插入第一级数据
            sql = 'insert into app_menucategory(name,brief,category_level,parent_category_id,category_way,islast_level)' \
                  ' values (%s, %s, %s, %s, %s, %s)'
            self.cursor.execute(sql, (name, brief, category_level, parent_category_id, category_way, islast_level))
            self.connect.commit()

            # 获取id
            sql = 'select id from app_menucategory where name = "' + name + '" and category_level = 1'
            self.cursor.execute(sql)
            self.connect.commit()
            result = self.cursor.fetchall()
            id = result[0][0]

            # 插入二级数据
            for child in childs:
                name = child['name']
                brief = child['name']
                category_level = child['level']
                parent_category_id = id
                category_way = child['leibie']
                islast_level = True
                extralurl = child['url']
                # 插入第二级数据
                sql = 'insert into app_menucategory(name,brief,category_level,parent_category_id,category_way,extralurl,islast_level)' \
                      ' values (%s, %s, %s, %s, %s, %s,%s)'
                self.cursor.execute(sql, (name, brief, category_level, parent_category_id, category_way,extralurl, islast_level))
                self.connect.commit()

        return item

    def close_spider(self, spider):
        self.connect.close()


class CaiDetailPipeline(object):
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
        )
        return cls(dbparams)

    @check_spider_pipeline
    def process_item(self, item, spider):
        name = item['name']
        brief = item['brief']
        tips = item['tips']
        views = item['views']
        collect = item['collect']
        makes = item['makes']
        burden = item['burden']
        img = item['img']

        # 如果已经存在 则不保存
        sql = 'select * from app_greens where name = "' + name + '"'
        row = self.cursor.execute(sql)
        self.connect.commit()
        if row == 0:
            # 插入数据
            sql = 'insert into app_greens(name, brief, tips, views, collect, makes, burden, img)' \
                  ' values (%s, %s, %s, %s, %s, %s, %s, %s)'
            self.cursor.execute(sql, (name, brief, tips, views, collect, makes, burden, img))
            self.connect.commit()
        else:
            print("已经存在，需要未该菜增加一个类型（操作关系表）")
        return item

    def close_spider(self, spider):
        self.connect.close()
