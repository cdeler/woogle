from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class WikiResponseProcessor(ABC):

    @abstractmethod
    def process(self, response):
        pass

    @staticmethod
    def getWikiResponseProcessor():
        args = 'File'
        if args == 'File':
            return FileWikiResponseProcessor()
        elif args == 'StdOut':
            return StdOutWikiResponseProcessor()


class FileWikiResponseProcessor(WikiResponseProcessor):
    def process(self, response, path=''):
        with open(f"texts//{response.xpath('//title/text()').extract_first()}.txt", 'w', encoding="utf-8") as output:
            try:
                text = response.xpath(
                    '//div[@class="mw-parser-output"]').extract()[0]
            except IndexError:
                return 0
            soup = BeautifulSoup(text, 'lxml')
            paragraph = soup.find('p')
            while True:
                output.write(paragraph.text)
                paragraph = paragraph.nextSibling
                if paragraph.name != "p":
                    break


class StdOutWikiResponseProcessor(WikiResponseProcessor):
    def process(self, response, n=40):
        output = ''
        print(response.url)
        try:
            text = response.xpath(
                '//div[@class="mw-parser-output"]').extract()[0]
        except BaseException:
            return 0
        soup = BeautifulSoup(text, 'lxml')
        paragraph = soup.find('p')
        while True:
            output += paragraph.text
            if len(output) > n:
                break
            paragraph = paragraph.nextSibling
            if paragraph.name != "p":
                break
        print(output[:n])
