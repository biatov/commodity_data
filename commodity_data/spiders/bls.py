import scrapy
from ..items import CommodityDataItem


class Bls(scrapy.Spider):
    name = 'bls'
    allowed_domains = ['data.bls.gov']
    start_urls = ['https://data.bls.gov/cgi-bin/dsrv?wp']
    main_url = start_urls[0].split('?')[0]
    get_data_url = 'https://data.bls.gov/pdq/SurveyOutputServlet'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'data.bls.gov',
        'Origin': 'https://data.bls.gov',
        'Referer': main_url,
        'Upgrade-Insecure-Requests': '1',
    }
    spec_headers = headers
    spec_headers['Referer'] = get_data_url

    def parse(self, response):
        level = response.xpath('//input[@name="level"]/@value').extract_first()
        survey = response.xpath('//input[@name="survey"]/@value').extract_first()
        body = f'seasonal=U&level={level}&survey={survey}&format=&html_tables=&delimiter=&catalog=&print_line_length=&lines_per_page=&row_stub_key=&year=&date=&net_change_start=&net_change_end=&percent_change_start=&percent_change_end='
        yield scrapy.FormRequest(
            url=self.start_urls[0],
            body=body,
            callback=self.parse_series,
            dont_filter=True
        )

    def parse_series(self, response):
        level = response.xpath('//input[@name="level"]/@value').extract_first()
        survey = response.xpath('//input[@name="survey"]/@value').extract_first()
        seasonal = response.xpath('//input[@name="seasonal"]/@value').extract_first()

        select = response.xpath('//select[@name="group_code"]/option/@value').extract()

        for option in select[1:17]:
            body = f'group_code={option}&level={level}&survey={survey}&seasonal={seasonal}&format=&html_tables=&delimiter=&catalog=&print_line_length=&lines_per_page=&row_stub_key=&year=&date=&net_change_start=&net_change_end=&percent_change_start=&percent_change_end='
            yield scrapy.FormRequest(
                url=self.main_url,
                body=body,
                headers=self.headers,
                callback=self.parse_category_series,
                dont_filter=True
            )

    def parse_category_series(self, response):
        level = response.xpath('//input[@name="level"]/@value').extract_first()
        survey = response.xpath('//input[@name="survey"]/@value').extract_first()
        seasonal = response.xpath('//input[@name="seasonal"]/@value').extract_first()
        group_code = response.xpath('//input[@name="group_code"]/@value').extract_first()

        select = response.xpath('//select[contains(@name, "item_code_")]/option/@value').extract()
        for option in select:
            body = f'item_code_{group_code}={option}&level={level}&survey={survey}&seasonal={seasonal}&group_code={group_code}&format=&html_tables=&delimiter=&catalog=&print_line_length=&lines_per_page=&row_stub_key=&year=&date=&net_change_start=&net_change_end=&percent_change_start=&percent_change_end='
            yield scrapy.FormRequest(
                url=self.main_url,
                body=body,
                headers=self.headers,
                callback=self.parse_ids_series,
                dont_filter=True
            )

    def parse_ids_series(self, response):
        id_ = response.xpath('//textarea[@name="seriesids"]/text()').extract_first(default='').strip()
        if id_:
            body = f'output_type=column&years_option=specific_years&from_year=2008&to_year=2018&output_view=data&periods_option=all_periods&output_format=html&delimiter=comma&reformat=true&request_action=get_data&initial_request=false&data_tool=dsrv&series_id={id_}&original_output_type=simple&original_annualAveragesRequested=false'
            yield scrapy.FormRequest(
                url=self.get_data_url,
                # body=body,
                formdata={
                    'output_type': 'column',
                    'years_option': 'specific_years',
                    'from_year': '2008',
                    'to_year': '2018',
                    'output_view': 'data',
                    'periods_option': 'all_periods',
                    'output_format': 'html',
                    'delimiter': 'comma',
                    'reformat': 'true',
                    'request_action': 'get_data',
                    'initial_request': 'false',
                    'data_tool': 'dsrv',
                    'series_id': id_,
                    'original_output_type': 'simple',
                    'original_annualAveragesRequested': 'false'
                },
                callback=self.parse_data,
                dont_filter=True
            )

    def parse_data(self, response):
        item = CommodityDataItem()
        series_id = response.xpath(
            '//table[@class="regular-data"]/caption//strong[contains(text(), "Series Id")]/following-sibling::text()[1]'
        ).extract_first(default='').strip()
        series_title = response.xpath(
            '//table[@class="regular-data"]/caption//strong[contains(text(), "Series Title")]'
            '/following-sibling::text()[1]'
        ).extract_first(default='').strip()
        group = response.xpath(
            '//table[@class="regular-data"]/caption//strong[contains(text(), "Group")]/following-sibling::text()[1]'
        ).extract_first(default='').strip()
        item_title = response.xpath(
            '//table[@class="regular-data"]/caption//strong[contains(text(), "Item")]/following-sibling::text()[1]'
        ).extract_first(default='').strip()
        base_date = response.xpath(
            '//table[@class="regular-data"]/caption//strong[contains(text(), "Base Date")]/following-sibling::text()[1]'
        ).extract_first(default='').strip()
        rows = response.xpath('//table[@class="regular-data"]/tbody/tr')
        for row in rows:
            item['series_id'] = series_id
            item['series_title'] = series_title
            item['group'] = group
            item['item'] = item_title
            item['base_date'] = base_date
            item['year'] = row.xpath('th[2]/text()').extract_first(default='').strip()
            item['period'] = row.xpath('th[3]/text()').extract_first(default='').strip()
            item['value'] = row.xpath('td/text()').extract_first(default='').strip()
            yield item
