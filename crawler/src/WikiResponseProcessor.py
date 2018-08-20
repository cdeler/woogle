from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os
import errno
import re

from src import database_binding as database_binding

NOT_USED_CHARACTERS_IN_DIRECTORY_MODE = [
    '/', '\\', ':', '*', '?', '"', '<', '>', '|']


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
                return DBResponseProcessor()

            else:
                raise ValueError(
                    f"Invalid mode output - {args['output']}. Correct value of argument 'output' - stdout, db, directory ")
        else:
            return DBWikiResponseProcessor()


class FileWikiResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to store crawled data in files   """

    def process(self, response, path=os.path.join(os.getcwd(), 'texts')):
        """ Method that prints article's snippet to file
        :param response: response to parse
        :param path: folder to save articles to
        :return: None
        """

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        # delete not used characters in title/text()
        title_text = response.xpath('//title/text()').extract_first()
        for ch in NOT_USED_CHARACTERS_IN_DIRECTORY_MODE:
            title_text = title_text.replace(ch, '')

        path = os.path.join(path, f"{title_text}.txt")
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

    def process(self, response, n=40, silent=False):
        """ Method that prints first n symbols of wiki article to stdout

        :param response: response to parse
        :param n: number of symbols to print
        :param silent:
        :return: None

        """
        output = ''
        n = int(n)
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

        if not silent:
            print("\n------\n", response.url, '\n', output[:n], "\n------\n")


class DBResponseProcessor(WikiResponseProcessor):
    """ Class, which allows to store crawled data in database   """

    def process(self, response, db=True, id_to_update=None):
        """ Method that stores data into database

        :param response: response to parse
        :param db:
        :param id_to_update: id of record that needs to be updated
        :return: None
        """

        session = database_binding.init_db()
        title = response.xpath('//title/text()').extract_first()
        url = response.url
        if database_binding.read(session=session, url=url):
            return 0

        base = url[:24]
        content = ''
        try:
            text = response.xpath(
                '//div[@class="mw-parser-output"]').extract()[0]
        except IndexError:
            return 0

        soup = BeautifulSoup(text, 'lxml')
        paragraph = soup.select('div.mw-parser-output > p')
        links = ''
        for p in paragraph:
            for link in p.findAll('a', attrs={'href': re.compile("^/wiki")}):
                full_link = base + link.get('href') + ' '
                links += full_link
            content += p.text
            if p.nextSibling.name != 'p':
                break

        #session = database_binding.init_db()

        if id_to_update:
            database_binding.update(
                session,
                id_to_update,
                title=title,
                url=url,
                text=content,
                links=links)
        else:
            database_binding.insert(
                session, title=title, url=url, text=content, links=links)
