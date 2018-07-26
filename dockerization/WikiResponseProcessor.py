from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os
import psycopg2


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


class DBResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to store crawled data in database   """

    def __init__(self):
        # names of existing database should be here to establish connection
        self.connection = psycopg2.connect(f"host='localhost' dbname='dbname' user='username' password='password'")

    def process(self, response, db=True):
        """ Method that stores data into database

        :param response
        :param db
        :return:
        """
        columns = 'title, url, content, pagerank'

        title = response.xpath('//title/text()').extract_first()
        url = response.url
        content = ''
        try:
            text = response.xpath(
                    '//div[@class="mw-parser-output"]').extract()[0]
        except IndexError:
            return 0

        soup = BeautifulSoup(text, 'lxml')
        paragraph = soup.find('p')
        while True:
            content += paragraph.text
            paragraph = paragraph.nextSibling
            if paragraph.name != "p":
                break

        values = (title, url, content, 0)
        mark = self.connection.cursor()
        # wikitable must be replaced by the real name of the table
        statement = 'INSERT INTO wikitable (' + columns + ') VALUES (%s,%s,%s,%s)'

        mark.execute(statement, values)
        self.connection.commit()