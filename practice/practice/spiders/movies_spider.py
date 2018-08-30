import scrapy


class MoviesSpider(scrapy.Spider):
    name = "movies"
    start_urls = [
        'http://hdpopcorns.co/',
    ]

    def parse(self, response):
        for movie in response.css('article.latestPost.excerpt'):
            movie_detail = {
                'Download Link': movie.css('a::attr(href)').extract_first(),
            }
            yield response.follow(movie_detail.get('Download Link'), callback=self.parse_movie_details)

    def parse_movie_details(self, response):
        movie_details = response.xpath('/html/body/div[1]/div/article/div/div[1]/div[1]/div[1]/div[2]')
        yield{
            'Title': movie_details.xpath('p[1]/text()').extract_first(),
            'Year': movie_details.xpath('p[3]/a[1]/text()').extract(),
            'Language': movie_details.xpath('p[3]/a[4]/text()').extract(),
            'Download Link': response.urljoin(""),
            'Thumb Nail': movie_details.xpath('p[2]/a/img/@src').extract(),
            'Synopsis': movie_details.xpath('p[7]/text()').extract(),

        }
