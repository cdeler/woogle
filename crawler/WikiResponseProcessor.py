from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os

from database_binding import init_db, insert, delete_all, update


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
    """ Class, which allows to store crawled data in files   """

    def process(self, response, path=os.path.join(os.getcwd(), 'texts')):
        """ Method that prints article's snippet to file
        :param response: response to parse
        :param path: folder to save articles to
        :return: None
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
            paragraph = soup.select('div.mw-parser-output > p')
            for p in paragraph:
                output.write(p.text)
                if p.nextSibling.name != 'p':
                    break


class StdOutWikiResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to print crawled data to standard output   """

    def process(self, response, n=40):
        """ Method that prints first n symbols of wiki article to stdout

        :param response: response to parse
        :param n: number of symbols to print
        :return: None
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
        for p in paragraph:
            output += p.text
            if len(output) > n or p.nextSibling.name != 'p':
                break
        print(output[:n])


class DBResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to store crawled data in database   """

    def process(self, response, db=True, id_to_update=None):
        """ Method that stores data into database

        :param response: response to parse
        :param db:
        :param id_to_update: id of record that needs to be updated
        :return: None
        """
        title = response.xpath('//title/text()').extract_first()
        url = response.url
        content = ''
        try:
            text = response.xpath(
                '//div[@class="mw-parser-output"]').extract()[0]
        except IndexError:
            return 0

        soup = BeautifulSoup(text, 'lxml')
        paragraph = soup.select('div.mw-parser-output > p')
        for p in paragraph:
            content += p.text
            if p.nextSibling.name != 'p':
                break

        session = init_db()

        if id_to_update:
            update(session, id_to_update, title=title, url=url, text=content)
        else:
            insert(session, title=title, url=url, text=content)
