import scrapy
import re
import json
from practice.items import EloquiiItem


class EeloquiiSpider(scrapy.Spider):
    name = 'eloquii'
    start_urls = ['https://www.eloquii.com/plus-size-t-shirts']

    def parse(self, response):
        sections = response.xpath('//*[@id="nav_menu"]/li')
        categories = []
        for section in sections:
            categories = categories + section.xpath('ul/li/div/p[1]/a/@href').extract()
        for category in categories:
            if category.find('https') != -1:
                yield response.follow(category, callback=self.parse_category)

    def parse_category(self, response):
        category = response.css("div.mb-5>div.col>div.row>div")
        products = category.xpath('div/a[1]')
        for product in products:
            product_id = product.xpath('@href').re(r'[\d]+\.')[0][:-1]
            product_url = product.xpath('@href').extract_first()

            product_details = "https://www.eloquii.com/on/demandware.store/Sites-eloquii-Site/default/" \
                              "Product-GetVariants?pid={}&format=json".format(product_id)
            yield response.follow(product_details, callback=self.parse_product_details,
                                  meta={'Product Name': product.xpath('img/@alt').extract_first(),
                                        'Product ID': product_id, 'Product Url': product_url,
                                        'Product Image': product.xpath('img/@src').extract_first()})

    def basic_product_details(self, json_response):
        raw_details = list()
        for variant in json_response["variations"]["variants"]:
            raw_details = raw_details + [[variant["attributes"]["colorCode"], variant["attributes"]["size"],
                                          {"Standard": variant["pricing"]["standard"],
                                           "Sale": variant["pricing"]["sale"]}]]
        details = list()
        iterator = 0
        while iterator < len(raw_details):
            color = raw_details[iterator][0]
            sizes = raw_details[iterator][1]
            pricing = raw_details[iterator][2]
            raw_details.remove(raw_details[iterator])
            counter = 0
            maxCount = len(raw_details)
            while counter < maxCount:
                if raw_details[counter][0] == color:
                    sizes = sizes + ", " + raw_details[counter][1]
                    raw_details.remove(raw_details[counter])
                    maxCount -= 1
                else:
                    counter += 1
            details = details + [{'Color': color, 'Available Sizes': sizes, 'Pricing': pricing}]

        return details

    def parse_product_details(self, response):
        json_response = json.loads(response.body_as_unicode())
        details = self.basic_product_details(json_response)
        items = EloquiiItem()
        items['name'] = response.meta['Product Name']
        items['ID'] = response.meta['Product ID']
        items['availability'] = details
        items['weblink'] = response.meta['Product Url']
        items['image'] = response.meta['Product Image']
        yield items

