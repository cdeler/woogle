from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os


class WikiResponseProcessor(ABC):

    @abstractmethod
    def process(self, response):
        pass

    @staticmethod
    def getWikiResponseProcessor(args=None):

        if args is not None and 'output' in args:
            mode_output = args['output']

            if mode_output == 'stdout':
                return StdOutWikiResponseProcessor()
            elif mode_output == 'directory':
                return FileWikiResponseProcessor()
            elif mode_output == 'db':
                # code for output in db
                print("Output mode: data base")
                pass
            else:
                raise ValueError(
                    f"Invalid mode output - {args['output']}. Correct value of argument 'output' - stdout, db, directory ")
        else:
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
    def process(self, response, n=40, silent=False):
        """ Method that prints first n symbols of wiki article to stdout

        :param response:
        :param n:
        :param silent:
        :return:
        """
        output = ''
        n = int(n)
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

        if not silent:
            print("\n------\n", response.url, '\n', output[:n], "\n------\n")
