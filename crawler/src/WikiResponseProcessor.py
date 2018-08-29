from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os
import errno
import re
import scrapy

from src import database_binding


NOT_USED_CHARACTERS_IN_DIRECTORY_MODE = [
    '/', '\\', ':', '*', '?', '"', '<', '>', '|']

session = database_binding.init_db()

class WikiResponseProcessor(ABC):

    @abstractmethod
    def process(self, response):
        pass

    @staticmethod
    def getWikiResponseProcessor(output):

        if output == 'stdout':
            return StdOutWikiResponseProcessor()
        elif output == 'directory':
            return FileWikiResponseProcessor()
        elif output == 'db':
            return DBResponseProcessor()
        else:
            raise ValueError(
                f"Invalid mode output - {output}. Correct value of argument 'output' - stdout, db, directory ")



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
            paragraph = soup.select('div.mw-parser-output > p')[0]
            while paragraph.text.strip() == '':
                paragraph = paragraph.find_next_sibling('p')
            while True:
                output.write(paragraph.text)
                if paragraph.next_sibling.name == 'p':
                    paragraph = paragraph.next_sibling
                else:
                    break

            print('-')



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
        paragraph = soup.select('div.mw-parser-output > p')[0]

        while paragraph.text.strip() == '':
            paragraph = paragraph.find_next_sibling('p')
        while True:
            output += paragraph.text
            if paragraph.next_sibling.name == 'p':
                paragraph = paragraph.next_sibling
            else:
                break
            if len(output) > n:
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
        title = response.xpath('//title/text()').extract_first()
        last_time_updated = response.xpath('//li[@id="footer-info-lastmod"]/text()').extract_first()

        if not database_binding.article_is_changed(session, title, last_time_updated) and not id_to_update:
            return 0
        url = response.url
        base = url[:24]
        content = ' '
        links = []
        state = "waiting"

        # session = database_binding.init_db()
        article_info = {'title': title, 'url': url, 'text': content, 'state': state, 'page_rank': 0, 'last_time_updated': last_time_updated}

        if id_to_update:
            database_binding.update(session, id_to_update, article_info)
        else:
            database_binding.insert(session, article_info)



    def process_download(self, response, id_to_update=None):
        title = response.xpath('//title/text()').extract_first()
        url = response.url
        last_time_updated = response.xpath('//li[@id="footer-info-lastmod"]/text()').extract_first()
        base = url[:24]
        content = ''
        state = "complete"
        try:
            text = response.xpath('//div[@class="mw-parser-output"]').extract()[0]
        except Exception:
            print("error")
            return 0

        soup = BeautifulSoup(text, 'lxml')

        try:
            paragraph = soup.select('div.mw-parser-output > p')[0]
        except Exception as e:
            return 0

        links = []

        while paragraph.text.strip() == '':
            tmp= paragraph.find_next_sibling('p')
            if tmp:
                paragraph=tmp
            else:
                break

        while True:
            content += paragraph.text
            for link in paragraph.findAll('a', attrs={'href': re.compile("^/wiki")}):
                # full_link = base + link.get('href') + ' '
                full_link = base + link.get('href')
                links.append(full_link)
            if paragraph.next_sibling.name == 'p':
                paragraph = paragraph.next_sibling
            else:
                break

        article_info = {'title': title, 'url': url, 'text': content, 'state':state, 'page_rank': 0, 'last_time_updated': last_time_updated}
        session = database_binding.init_db()
        database_binding.update(session, id_to_update, article_info)
        database_binding.add_links(session, id_to_update, links)

        print('-')