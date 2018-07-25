import scrapy
from WikiResponseProcessor import *
import os


class WikiSpider(scrapy.Spider):
    name = 'WikiSpider'

    start_urls = [
        'https://ru.wikipedia.org/w/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%81%D0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
    ]

    allowed_domains = ['ru.wikipedia.org', ]

    def __init__(self, arg=None):
        super(WikiSpider, self).__init__()
        self.args = arg

    def parse(self, response):
        """ Method that parses page of wiki articles' list

        :param response:
        :return:
        """
        yield from self.parse_wiki_pages(response)

        next_page = response.xpath(
            '//a[contains(text(), "Следующая страница")]/@href').extract_first()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_wiki_pages(self, response):
        """ Method that calls parsing processor for wiki articles

        :param response:
        :return:
        """
        if self.args:
            self.processor = WikiResponseProcessor.getWikiResponseProcessor(
                self.args)
            self.processor.process(response, self.args)
        else:
            self.processor = WikiResponseProcessor.getWikiResponseProcessor()
            self.processor.process(response)

        pages = response.xpath(
            '//ul[@class="mw-allpages-chunk"]//a/@href').extract()
        for page in pages:
            if page is not None:
                yield response.follow(page, callback=self.parse_wiki_pages)
