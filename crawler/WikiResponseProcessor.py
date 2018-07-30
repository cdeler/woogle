from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os

from database_binding import init_db, insert, delete_all


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
            elif args == "db":
                processor_type = 'DBWRP'
        except AttributeError:
            pass

        if processor_type == 'StdOutWRP':
            return StdOutWikiResponseProcessor()
        elif processor_type == 'FileWRP':
            return FileWikiResponseProcessor()
        elif processor_type == 'DBWRP':
            return DBResponseProcessor()


class FileWikiResponseProcessor(WikiResponseProcessor):
    def process(self, response, path=os.path.join(os.getcwd(), 'texts')):
        """ Method that prints article's snippet to file
        :param response:
        :param path:
        :return:
        """
        path = os.path.join(path, f"{response.xpath('//title/text()').extract_first()}.txt")
        with open(path, 'w', encoding="utf-8") as output:
            try:
                text = response.xpath('//div[@class="mw-parser-output"]').extract_first()
                text = response.css('div.mw-parser-output').extract_first()
                # output.write(text)
            except IndexError:
                return 0
            soup = BeautifulSoup(text, 'lxml')
            paragraph = soup.find('p', recursive=False)
            # print(f'\n\n\n{paragraph}\n\n\n')
            # print(paragraph)
            print()
            # paragraph = soup.find('p')
            # output.write(soup.text)
            # paragraph = soup.find_next_sibling('p')
            while True:
                output.write(paragraph.text)
                paragraph = paragraph.nextSibling
                if paragraph.name != "p":
                    break

            # paragraph = soup.select('div.mw-parser-output > p')
            # for p in paragraph:
            #     output.write(p.text)
            #     if p.nextSibling.name != 'p':
            #         break


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
        paragraph = soup.select('div.mw-parser-output > p')
        # paragraph = soup.find('p')
        for p in paragraph:
            output += p.text
            if len(output) > n or p.nextSibling.name != 'p':
                break
        print(output[:n])


class DBResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to store crawled data in database   """

    def process(self, response, db=True):
        """ Method that stores data into database
        :param response
        :param db
        :return:
        """

        title = response.xpath('//title/text()').extract_first()
        url = response.url
        content = ''
        try:
            text = response.xpath('//div[@class="mw-parser-output"]').extract()[0]
        except IndexError:
            return 0

        soup = BeautifulSoup(text, 'lxml')
        paragraph = soup.select('div.mw-parser-output > p')
        for p in paragraph:
            content += p.text
            if p.nextSibling.name != 'p':
                break

        session = init_db()
        insert(session, title=title, url=url, text=content)