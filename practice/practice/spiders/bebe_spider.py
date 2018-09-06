import scrapy


class BebeSpider(scrapy.Spider):
    name = 'bebe'
    start_urls = ['http://www.bebe.com', ]

    def parse(self, response):
        for dress_section in response.xpath('//ul[@id="topNavRoot"]/li/a/@href').extract():
            if dress_section.find('sec') != -1:
                yield response.follow(dress_section, callback=self.parse_section)

    def parse_section(self, response):
        for category in response.xpath('/html/body/div[1]/div[2]/nav/div/div[1]/ul/li/div/a/@href').extract():
            if category.find('cat') != -1:
                yield response.follow(category, callback=self.parse_product)

    def parse_product(self, response):
        p = len(response.xpath('/html/body/div[1]/div[2]/div/div[4]/div[1]/div/div/div/div/a/@href').extract())
        for product in response.xpath('/html/body/div[1]/div[2]/div/div[4]/div[1]/div/div/div/div/a/@href').extract():
            yield response.follow(product, callback=self.parse_product_details)

    def parse_product_details(self, response):
        basic_details = response.request.url
        basic_details = basic_details.split('/')
        section = basic_details[basic_details.index('www.bebe.com') + 1]
        category = basic_details[basic_details.index('www.bebe.com') + 2]
        product_name = basic_details[basic_details.index('www.bebe.com') + 3]

        details = response.xpath('//*[@id="description-container"]')
        style_code = details.css('div.item-no.uppercase.spaced::text').extract()

        if section != "Sale":
            actual_price = details.css('p.priceDisplay span.currentPrice::text').extract()
            if len(actual_price) >= 2:
                actual_price = actual_price[0] + actual_price[1]
            discounted_price = 'Not Applicabe'
        else:
            actual_price = details.css('p.priceDisplay span.basePrice::text').extract()
            if len(actual_price) >= 2:
                actual_price = actual_price[0] + actual_price[1]

            discounted_price = details.css('p.priceDisplay span.salePrice::text').extract_first() + \
                               details.css('p.priceDisplay span.salePrice span::text').extract_first()

        description = response.xpath('//div[@class="description"]/text()').extract()
        characteristics = response.xpath('//div[@id="center-10"]/ul/li/text()').extract()

        yield {
            'Section': section,
            'Category': category,
            'Product Name': product_name,
            'Style Code': style_code,
            'Actual Price': actual_price,
            'Discounted Price': discounted_price,
            'Description': description,
            'Product Characteristics:': characteristics,

        }
