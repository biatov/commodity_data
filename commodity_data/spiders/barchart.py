import scrapy
from ..items import CommodityDataItem


class Barchart(scrapy.Spider):
    name = 'barchart'
    allowed_domains = ['barchart.com']
    start_urls = ['https://www.barchart.com/proxies/timeseries/queryeod.ashx?symbol=ZLY00&data=monthly&start=20080101&volume=total&order=asc&dividends=false&backadjust=false&daystoexpiration=1&contractroll=expiration']

    def parse(self, response):
        item = CommodityDataItem()
        data = response.text
        data = list(filter(None,
                           [list(filter(None, [i.strip() for i in candle.split(',')])) for candle in data.split('\n')]))
        for candle in data:
            item['series_id'] = candle[0]
            item['series_title'] = 'Soybean Oil'
            item['date'] = candle[1]
            item['close'] = candle[5]
            item['source_index'] = 'CBOT Soybean'
            yield item
