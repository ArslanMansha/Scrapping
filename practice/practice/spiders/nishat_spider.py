import scrapy

class NishatSpider(scrapy.Spider):
    name = 'nishat'
    start_urls = ['http://nishatlinen.com/pk/home']

    def parse(self, response):
        categories = response.xpath('//div[@class="drop-holder"]/ul/li/a/@href').extract()
        #sections = response.xpath('//div[@id="store.menu"]/nav[@data-action="navigation"]/ul/li/ul/li/a/@href').extract()
        sections = categories #+ sections
        for section in sections:
            yield response.follow(section, callback=self.parse_category)

    def parse_category(self, response):
        products = response.xpath('//div[@class="product-item-info"]/a/@href').extract()
        for product in products:
            yield response.follow(product, callback=self.parse_product)

        if response.css('a.action.next::attr(href)').extract_first() is not None:
            yield response.follow(response.css('a.action.next::attr(href)').extract_first(), callback=self.parse_category)
        #subsections = response.xpath('//div[@class="filter-options"]/div[1]/div/ol/li/a')

    def parse_product(self, response):
        yield {'name': response.xpath('/html/body/div[1]/main/div[2]/div/div/div[2]/div/section/div[2]/div/div[1]/h1/span').extract_first()}