# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv


class CommodityDataPipeline(object):
    def __init__(self):
        self.file = csv.writer(open('demo.csv', 'w'), quoting=csv.QUOTE_MINIMAL)
        self.file.writerow(
            ['Series Id', 'Series Title', 'Group', 'Item', 'Base Date', 'Year', 'Period', 'Value']
        )

    def process_item(self, item, spider):
        self.file.writerow([
            item['series_id'],
            item['series_title'],
            item['group'],
            item['item'],
            item['base_date'],
            item['year'],
            item['period'],
            item['value'],
        ])
        return item
1