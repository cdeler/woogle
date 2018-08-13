import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
import datetime

import crawler.WikiResponseProcessor as WikiResponseProcessor
import crawler.setting_language as setting
import crawler.database_binding as database_binding


STATE_CRAWLER = {1: 'Working',
                 2: 'Shutdown',
                 3: 'Finished'}

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'LOG_FILE': 'log.txt',
    'LOG_LEVEL': 'INFO'
})


def arg_str2dict(arg):
    """
    Converting argument from "arg1=va1 arg2=val2 ..." to dict {arg1:va1, arg2:val2, ...}
    :param args: str
    :return: dict
    """
    try:
        arg_dict = {i.split('=')[0]: i.split('=')[1] for i in arg.split()}
    except Exception as e:
        raise TypeError(
            "Invalid format argument:\n f{arg} \n Correct format: 'arg1=va1 arg2=val2 ...' ") from e

    if 'silent' in arg_dict:
        if arg_dict['silent'] == "False":
            arg_dict['silent'] = False
        elif arg_dict['silent'] == "True":
            arg_dict['silent'] = True
        else:
            raise ValueError(
                f"Invalid mode silent - {arg_dict['silent']}. Correct value of argument 'silent' - True, False ")

    return arg_dict


def choose_language(arg):
    # setup language setting
    languages = list(setting.LANGUAGE_SETTING.keys())

    # default
    language_default = languages[0]

    if arg is not None and 'language' in arg:
        if arg['language'] in languages:
            return arg['language']
        else:
            raise ValueError(
                f"Value of argument 'language' - {self.args['language']} is invalid. Correct value - {languages}")
    else:
        return language_default


class WikiSpider(scrapy.Spider):
    name = 'WikiSpider'

    def __init__(self, stats, arg=None):
        """
        Getting next arguments in format: arg1=va1 arg2=val2 ...":
            num_threads: count threads
            language: wikipedia language (ru, en)
            output: output (stdout, db, directory)
            silent: flag, turn on silent mode, use with output=stdout
        if one of the arguments is not specified, the following next value:
            language=ru
            output=directory
            silent=False

        :param arg: agrument for crawler
        :type arg: str
        """
        super(WikiSpider, self).__init__()
        if arg is not None:
            self.args = arg_str2dict(arg)
        else:
            self.args = arg

        # setup language setting
        self.language = choose_language(self.args)

        self.start_urls = [
            setting.LANGUAGE_SETTING[self.language]['start_urls']]
        self.allowed_domains = [
            setting.LANGUAGE_SETTING[self.language]['allowed_domains']]
        self.next_page_words = setting.LANGUAGE_SETTING[self.language]['next_page_words']

        # stats
        self.stats = stats
        self.stats.set_value('current_page', self.start_urls[0])
        self.stats.set_value('pages_crawled', 0)

        self.add_start_info_db()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.stats, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        """ Method that parses page of wiki articles' list

        :param response:
        :return:
        """
        # stats
        self.stats.set_value('current_page', response.url)
        self.add_curr_info_db()
        yield from self.parse_wiki_pages(response)

        next_page = response.xpath(
            f'//a[contains(text(), "{self.next_page_words}")]/@href').extract_first()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        else:
            self.stats.set_value('current_page', None)

    def parse_wiki_pages(self, response):
        """ Method that calls parsing processor for wiki articles

        :param response:
        :return:
        """

        self.processor = WikiResponseProcessor.WikiResponseProcessor.getWikiResponseProcessor(
            self.args)
        # stats
        self.stats.inc_value('pages_crawled')

        if self.args and 'output' in self.args:
            if self.args['output'] == 'stdout' and 'silent' in self.args:
                self.processor.process(response, silent=self.args['silent'])
            else:
                self.processor.process(response)
        else:
            self.processor.process(response)

        pages = response.xpath(
            '//ul[@class="mw-allpages-chunk"]//a/@href').extract()
        for page in pages:
            if page is not None:
                yield response.follow(page, callback=self.parse_wiki_pages)

    def add_start_info_db(self):
        """
        Add start informations to database
        Start informations:
               start_time: start date and start time
               language: wikipedia languag
               pages_crawled: count crawled pages
               current_page: current url page with article
               state and state_id: state crawler from STATE_CRAWLER
        :return: None
        """
        # write in database
        self.db_actions = database_binding.CrawlerStatsActions()
        self.db_actions.create(
            start_time=str(datetime.datetime.now()),
            language=self.language,
            pages_crawled=0,
            current_page=self.start_urls[0],
            state_id=1,
            state=STATE_CRAWLER[1])

    def add_curr_info_db(self):
        """
        Add current informations to database
        Current informations:
               pages_crawled: count crawled pages
               current_page: current url page with article
        :return: None
        """
        self.db_actions.update(
            pages_crawled=self.stats.get_value('pages_crawled'),
            current_page=self.stats.get_value('current_page'))

    def add_finish_info_db(self, reason):
        """
         Add start informations to database
         Start informations:
                pages_crawled: count crawled pages
                current_page: current url page with article
                state and state_id: state crawler from STATE_CRAWLER
                finish_time: finish time
                finish_reason: finish reason from stats
         :return: None
         """
        if self.stats.get_value('current_page'):
            self.db_actions.update(
                pages_crawled=self.stats.get_value('pages_crawled'),
                current_page=self.stats.get_value('current_page'),
                state_id=2,
                state=STATE_CRAWLER[2],
                finish_time=datetime.datetime.now(),
                finish_reason=reason)
        else:
            self.db_actions.update(
                pages_crawled=self.stats.get_value('pages_crawled'),
                current_page=self.stats.get_value('current_page'),
                state_id=3,
                state=STATE_CRAWLER[3],
                finish_time=datetime.datetime.now(),
                finish_reason=reason)

    def closed(self, reason):
        self.add_finish_info_db(reason)
