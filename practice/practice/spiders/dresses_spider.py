import scrapy
import re


class DressesSpider(scrapy.Spider):
    name = 'dresses'
    start_urls = ['http://www.bebe.com', ]

    def parse(self, response):
        for dress_category in response.xpath('//ul[@id="topNavRoot"]/li/a/@href').extract():
            if dress_category.find('sec') != -1:
                yield response.follow(dress_category, callback=self.parse_category)

    def parse_category(self,response):
        for dress_sub_category in response.xpath('/html/body/div[1]/div[2]/nav/div/div[1]/ul/li/div/a/@href').extract():
            if dress_sub_category.find('cat') != -1:
                yield response.follow(dress_sub_category, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        for item in response.xpath('/html/body/div[1]/div[2]/div/div[4]/div[1]/div/div/div/div/a/@href').extract():
            yield response.follow(item, callback=self.parse_item_details)

    def parse_item_details(self,response):
        availabe_sizes = response.xpath('')

        basic_item_details = response.request.url
        basic_item_details = basic_item_details.split('/')
        start_index = basic_item_details('www.bebe.com')+1
        yield{
            'Section': basic_item_details[start_index],
            'Category': basic_item_details[start_index+1],
            'Item Name': basic_item_details[start_index+2],

        }
