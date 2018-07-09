import scrapy
from bs4 import BeautifulSoup


class WikiSpider(scrapy.Spider):
    name = 'WikiSpider'

    start_urls = [
        'https://ru.wikipedia.org/'
    ]

    allowed_domains = ['ru.wikipedia.org', ]

    def parse(self, response):
        with open(f"texts//{response.xpath('//title/text()').extract_first()}", 'w', encoding="utf-8") as output:
            for text in response.xpath("//p").extract():
                clean_text = BeautifulSoup(text, "lxml").text
                output.write(clean_text)

        pages = response.css('a::attr(href)').extract()
        for page in pages:
            if page is not None:
                yield response.follow(page, callback=self.parse)
