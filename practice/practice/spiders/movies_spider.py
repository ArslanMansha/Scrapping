import scrapy
import re

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
        quality = movie_details.xpath('p[3]').re(r'>[0-9]+p<')
        for iterator in range(len(quality)):
            if len(quality[iterator]) > 5:
                quality[iterator] = quality[iterator][1:-1]

        language = movie_details.xpath('p[3]').re(r'Language[\s\w\W]*Genre')
        language = re.findall(r'>[\w\s]+<', str(language))
        for iterator in range(len(language)):
            language[iterator] = language[iterator][1:-1]
        # language.remove(' ')

        genre = movie_details.xpath('p[3]').re(r'Genre[\s\w\W]*Cast')
        genre = re.findall(r'>[\w\s]+<', str(genre))
        for iterator in range(len(genre)):
            genre[iterator] = genre[iterator][1:-1]
        # genre.remove(' ')

        cast = movie_details.xpath('p[3]').re(r'Cast[\s\w\W]*imdb/')
        cast = re.findall(r'>[\w\s]+<', str(cast))
        for iterator in range(len(cast)):
            cast[iterator] = cast[iterator][1:-1]
        # cast.remove(' ')

        imdb_rating = movie_details.xpath('p[3]').re(r'strong>[\d\.]*</strong')
        imdb_rating = re.findall(r'>[\d\.]*<', str(imdb_rating))
        imdb_rating = imdb_rating[0][1:-1]

        synopsis = movie_details.xpath('p[3]').re(r'Synopsis[\s\w\W]*</p>')
        synopsis = re.findall(r'>[\w\W]*<', str(synopsis))
        synopsis = synopsis[0][1:-1]

        yield {
            'Title': movie_details.xpath('p[1]/text()').extract_first(),
            'Year': movie_details.xpath('p[3]').re(r'>[0-9]{4}<')[0][1:5],
            'Quality': quality,
            'Language': language,
            'Genre': genre,
            'Cast': cast,
            'IMDB rating': imdb_rating,
            # 'Download Link': response.urljoin(""),
            # 'Thumb Nail': movie_details.xpath('p[2]/a/img/@src').extract(),
            'Synopsis': synopsis,

        }
