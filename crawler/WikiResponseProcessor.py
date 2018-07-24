from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os


class WikiResponseProcessor(ABC):

    @abstractmethod
    def process(self, response):
        pass

    @staticmethod
    def getWikiResponseProcessor(args=None):
        processor_type = 'FileWRP'
        try:
            if args.isdigit():
                processor_type = 'StdOutWRP'
        except AttributeError:
            pass

        if processor_type == 'StdOutWRP':
            return StdOutWikiResponseProcessor()
        elif processor_type == 'FileWRP':
            return FileWikiResponseProcessor()


class FileWikiResponseProcessor(WikiResponseProcessor):
    def process(self, response, path=os.path.join(os.getcwd(), 'texts')):
        """ Method that prints article's snippet to file

        :param response:
        :param path:
        :return:
        """
        path = os.path.join(
            path, f"{response.xpath('//title/text()').extract_first()}.txt")
        with open(path, 'w', encoding="utf-8") as output:
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
        """ Method that prints first n symbols of wiki article to stdout

        :param response:
        :param n:
        :return:
        """
        output = ''
        n = int(n)
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
