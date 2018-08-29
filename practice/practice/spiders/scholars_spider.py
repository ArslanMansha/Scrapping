import scrapy


class ScholarsSpider(scrapy.Spider):
    name = 'scholars'
    start_urls = ['https://scholars.arbisoft.com/']

    def parse(self, response):
        for scholar in response.css('div.card'):
            info = scholar.css('ul.info-list.list-unstyled > li::text').extract()
            yield {
                'Image Source': scholar.css('div.img-holder > img::attr(src)').extract(),
                'Name': scholar.css('div.info>h3::text').extract(),
                'Study Program': info[0],
                'Status': info[1],
                'linkedIn Profile': scholar.css('li.linkedin > a::attr(href)').extract(),
            }
