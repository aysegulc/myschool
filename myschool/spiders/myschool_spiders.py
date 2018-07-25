# -*- coding: utf-8 -*-
import scrapy
import json
import csv
import pkgutil
from StringIO import StringIO

#with open('au_zipcodes.csv') as f:
csvdata = pkgutil.get_data("myschool", "resources/" + 'au_zipcodes.csv')
csvio = StringIO(csvdata)
read = csv.reader(csvio)
reader_list = [row for row in read]
zip_list = [row[0] for row in reader_list[1:]]


class MyschoolSpider(scrapy.Spider):
    name = "myschool"
    allowed_domains = ["myschool.edu.au"]
    start_urls = ['https://myschool.edu.au/']

    def parse(self, response):
        for code in zip_list:
            yield scrapy.Request('https://myschool.edu.au/SchoolSearch/GlobalSearch?term='
                                 + code + '&count=20', self.parse_search)

    def parse_search(self, response):
        listings = json.loads(response.text)
        for listing in listings[-1:]:
            request = scrapy.Request('https://myschool.edu.au/Home/Index/' + listing['SMCLID'],
                                     self.parse_profile)
            request.meta['school'] = listing['SchoolDetails']
            request.meta['year'] = '2016'
            request.meta['start'] = 1
            yield request

    def parse_profile(self,response):
        school = response.meta['school']
        start = response.meta['start']

        if start:
            year = response.xpath('//li[contains(@class,"ui-state-active")]/a/text()').extract_first(default=response.meta['year'])
        else:
            year = response.meta['year']

        if start:
            other_years = response.xpath('//li[contains(@class,"ui-state-default")]/a/@href').extract()
            for link in other_years:
                link = link.split('?')[0]
                link_year = link.split('/')[-1]
                link = link.replace('/Home/TabControl', 'https://myschool.edu.au/SchoolProfile/Index')
                request = scrapy.Request(link, self.parse_profile)
                request.meta['school'] = school
                request.meta['year'] = link_year
                request.meta['start'] = 0
                yield request
            # finance request
            finance_link = response.xpath(
                '//ul[@id="SideMenu"]/li/a[contains(@href,"Finance")]/'
                '@href').extract_first(default='')
            if finance_link:
                request = scrapy.Request('https://myschool.edu.au' + finance_link, self.parse_finance)
                request.meta['school'] = school
                request.meta['year'] = '2016'
                request.meta['start'] = 1
                yield request

            # naplan request: results in numbers
            naplan_link = response.xpath(
                '//li[@id="NaplanMenu"]//li/a[contains(@href,"ResultsInNumbers")]/'
                '@href').extract_first(default='')
            if naplan_link:
                request = scrapy.Request('https://myschool.edu.au' + naplan_link, self.parse_naplan)
                request.meta['school'] = school
                request.meta['year'] = '2016'
                request.meta['start'] = 1
                yield request

            ## vet request: results in numbers
            vet_link = response.xpath('//ul[@id="SideMenu"]/li/a[contains(@href,"VetInSchools")]/@href').extract_first(default='')
            if vet_link:
                request = scrapy.Request('https://myschool.edu.au' + vet_link, self.parse_vet)
                request.meta['school'] = school
                request.meta['year'] = '2016'
                request.meta['start'] = 1
                request.meta['type'] = 1
                yield request

        ####data scrape
        boxes = response.xpath('//div[@class="profile-box"][not(@style)]')
        data_list = []

        for box in boxes:
            box_dict = dict()
            box_dict['header'] = box.xpath('h2/text()').extract_first()
            table = []
            for item in box.xpath('table//tr'):
                table.append([i.strip() for i in item.xpath('th/text()').extract()
                             + item.xpath('td/text()').extract() +
                             item.xpath('td/a/text()').extract() +
                             item.xpath('td/a/@href').extract()])
            box_dict['table'] = table
            data_list.append(box_dict)
        yield {
            'data': data_list,
            'url': response.url,
            'school': school,
            'type': 'profile',
            'year': year,
        }

    def parse_finance(self,response):
        school = response.meta['school']
        start = response.meta['start']

        if start:
            year = response.xpath('//li[contains(@class,"ui-state-active")]/a/text()').extract_first(default=response.meta['year'])
        else:
            year = response.meta['year']

        if start:
            other_years = response.xpath('//li[contains(@class,"ui-state-default")]/a/@href').extract()
            for link in other_years:
                link = link.split('?')[0]
                link_year = link.split('/')[-1]
                link = link.replace('/Home/TabControl','https://myschool.edu.au/Finance/Index')
                request = scrapy.Request(link, self.parse_finance)
                request.meta['school']  = school
                request.meta['year'] = link_year
                request.meta['start'] = 0
                yield request

        # data scrape
        boxes = response.xpath('//table[@class="finance-table"]')
        data_list = []

        for box in boxes:
            box_dict = dict()
            box_dict['header'] = box.xpath('thead/tr/th//text()').extract()
            table = []
            for item in box.xpath('tbody/tr'):
                table.append([i.strip() for i in item.xpath('td//text()').extract()])
            box_dict['table']=table
            data_list.append(box_dict)

        yield {
            'data': data_list,
            'url': response.url,
            'school': school,
            'type': 'finance',
            'year': year,
        }

    def parse_naplan(self,response):
        school = response.meta['school']
        start = response.meta['start']

        if start:
            year = response.xpath('//li[contains(@class,"ui-state-active")]/a/text()').extract_first(default=response.meta['year'])
        else:
            year = response.meta['year']

        if start:
            other_years = response.xpath('//li[contains(@class,"ui-state-default")]/a/@href').extract()
            for link in other_years:
                link = link.split('?')[0]
                link_year = link.split('/')[-1]
                link = link.replace('/Home/TabControl','https://myschool.edu.au/ResultsInNumbers/Index')
                request = scrapy.Request(link, self.parse_naplan)
                request.meta['school'] = school
                request.meta['year'] = link_year
                request.meta['start'] = 0
                yield request

        # data scrape
        boxes = response.xpath('//div[@id="ResultsInNumbersContainer"]/table')
        data_list = []

        for box in boxes:
            box_dict = dict()
            keys = box.xpath('thead/tr/th/text()').extract()
            box_dict['keys'] = keys
            table = []
            for item in box.xpath('tbody/tr[@class="selected-school-row"]'):
                row = dict()
                row['header'] = item.xpath('th/text()').extract()
                row['school'] = dict()
                for i, field in enumerate(item.xpath('td')):
                    row['school'][keys[i]] = field.xpath('span/text()').extract()
                color_list = [i.xpath('img/@alt').extract_first(default='') for i in item.xpath('following-sibling::tr[1]/td')]
                if color_list:
                    if len(color_list) > 5:
                        row['color'] = {k: color_list[2*i: 2*i+2] for i, k in enumerate(keys)}
                    else:
                        row['color'] = {k: [color_list[i]] for i, k in enumerate(keys)}
                sim_list = []
                for i, field in enumerate(item.xpath('following-sibling::tr[2]/td')):
                    sim_list.append(field.xpath('span/text()').extract())
                row['sim'] = {k: sim_list[2*i: 2*i+2] for i, k in enumerate(keys)}
                table.append(row)
            box_dict['table'] = table
            data_list.append(box_dict)

        yield {
            'data': data_list,
            'url': response.url,
            'school': school,
            'type': 'naplan',
            'year': year,
        }

    def parse_vet(self, response):
        school = response.meta['school']
        start = response.meta['start']
        vet_type = response.meta['type']

        if start:
            year = response.xpath('//li[contains(@class,"ui-state-active")]/a/text()').extract_first(default=response.meta['year'])
        else:
            year = response.meta['year']

        if start:
            other_years = response.xpath('//li[contains(@class,"ui-state-default")]/a/@href').extract()
            for link in other_years:
                link = link.split('?')[0]
                link_year = link.split('/')[-1]
                link = link.replace('/Home/TabControl','https://myschool.edu.au/VetInSchools/Index')
                request = scrapy.Request(link, self.parse_vet)
                request.meta['school'] = school
                request.meta['year'] = link_year
                request.meta['start'] = 0
                request.meta['type'] = 1
                yield request

        if vet_type:
            request = scrapy.FormRequest(response.url, formdata = {'VETActivityType':'2'}, callback=self.parse_vet)
            #request = scrapy.FormRequest('https://myschool.edu.au'+response.xpath('//li[contains(@class,"ui-state-active")]/a/@href').extract_first(), formdata = {'VETActivityType':'2'}, dont_filter=True)
            print response.url
            request.meta['school'] = school
            request.meta['year'] = year
            request.meta['start'] = 0
            request.meta['type'] = 0
            yield request

        # data scrape
        boxes = response.xpath('//table[@id="VetTable"]')
        data_list = []

        for box in boxes:
            box_dict = dict()
            box_dict['header'] = box.xpath('//thead/tr[last()]/th//text()').extract()
            table = []
            for item in box.xpath('tbody/tr'):
                table.append({'industry': [i.strip() for i in item.xpath('th/text()').extract() if i.strip()],
                              'data': [j.xpath('text()').extract_first(default='') for j in item.xpath('td')],
                              'main': [True for i in item.xpath('th[@class="toggle"]').extract()]})

            if box_dict['header'] and not table:
                box_dict['header'] = [i.strip() for i in box.xpath('//thead/tr[last()]/th//text()').extract() if i.strip()]
                table.append({'data': [[j.strip() for j in k.xpath('td//text()').extract()] for k in box.xpath('tr')]})

            box_dict['table'] = table
            data_list.append(box_dict)

        page_type = 'vet-enrolments' if vet_type else 'vet-qualifications'
        print page_type

        yield {
            'data': data_list,
            'url': response.url,
            'school': school,
            'type': page_type,
            'year': year,
        }
