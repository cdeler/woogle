import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
import datetime
import logging

from src import WikiResponseProcessor as WikiResponseProcessor
from src import setting_language as setting
from src import database_binding as database_binding

STATE_CRAWLER = {'Working': 1,
                 'Shutdown': 2,
                 'Finished': 3,
                 'Delegated': 4}

process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL':'INFO',
        'DOWNLOAD_DELAY': 0.2
})

def get_process(log_file,log_level,jobdir):
    setting={}
    if log_file:
        setting.update({'LOG_FILE':log_file})
    if log_level:
        setting.update({'LOG_LEVEL': log_level})
    if jobdir:
        setting.update({'JOBDIR': log_level})
    process.settings.update(setting)
    return process

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
                f"Value of argument 'language' - {arg['language']} is invalid. Correct value - {languages}")
    else:
        return language_default


class WikiSpider(scrapy.Spider):
    name = 'WikiSpider'

    def __init__(self, stats=None,language='ru',output='db',silent=False):
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

        self.output=output
        self.silent=silent
        # init language
        self.language = choose_language(language)
        # stats
        self.stats = stats
        # init languge params (next page, start page, etc.)
        self.init_params()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.stats, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.opened,signal=signals.spider_opened)
        return spider

    def parse(self, response):
        """ Method that parses page of wiki articles' list

        :param response:
        :return:
        """
        # stats
        self.stats.set_value('current_page', response.url)
        # database
        self.add_curr_info_db()

        pages = response.xpath(
            '//ul[@class="mw-allpages-chunk"]//a/@href').extract()

        for page in pages:
            if page is not None:
                yield response.follow(page, callback=self.parse_wiki_pages,priority=response.request.priority+1)

        next_page = response.xpath(
            f'//a[contains(text(), "{self.next_page_words}")]/@href').extract_first()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse,priority=response.request.priority)
        else:
            # stats
            self.stats.set_value('current_page', None)
            # database
            self.add_curr_info_db()
            
    def parse_wiki_pages(self, response):
        """ Method that calls parsing processor for wiki articles

        :param response:
        :return:
        """
        self.processor = WikiResponseProcessor.WikiResponseProcessor.getWikiResponseProcessor(
            self.output)

        if self.output == 'stdout':
            self.processor.process(response, silent=self.silent)
        else:
            if self.processor.process(response):
                self.stats.inc_value('pages_crawled')


    def init_params(self):
        logging.info('Init language options')

        self.allowed_domains = [
            setting.LANGUAGE_SETTING[self.language]['allowed_domains']]
        self.next_page_words = setting.LANGUAGE_SETTING[self.language]['next_page_words']

        if self.output == 'db':
            # get shutdown_crawler
            shutdown_crawler = database_binding.CrawlerStatsActions.get_shutdown_crawler(
                self.language, STATE_CRAWLER['Shutdown'])

            # if shutdown crawler is exist
            if shutdown_crawler:
                logging.info(
                    f"Selected shutdown crawler with id: {shutdown_crawler.instance.id}")
                self.start_urls = [shutdown_crawler.instance.current_page]
                self.stats.set_value(
                    'pages_crawled',
                    shutdown_crawler.instance.pages_crawled)

                shutdown_crawler.update(
                    state='Delegated',
                    state_id=STATE_CRAWLER['Delegated'])

            else:
                logging.info("Init new crawler")
                self.start_urls = [
                    setting.LANGUAGE_SETTING[self.language]['start_urls']]
                self.stats.set_value('pages_crawled', 0)
        else:
            logging.info("Init new crawler")
            self.start_urls = [
                setting.LANGUAGE_SETTING[self.language]['start_urls']]
            self.stats.set_value('pages_crawled', 0)

        self.stats.set_value('current_page', self.start_urls[0])


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
        if self.output == 'db':
            self.db_actions = database_binding.CrawlerStatsActions()
            self.db_actions.create(
                start_time=str(datetime.datetime.now()),
                language=self.language,
                pages_crawled=0,
                current_page=self.start_urls[0],
                state_id=STATE_CRAWLER['Working'],
                state='Working')

    def add_curr_info_db(self):
        """
        Add current informations to database
        Current informations:
               pages_crawled: count crawled pages
               current_page: current url page with article
        :return: None
        """
        if self.output == 'db':
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
        if self.output == 'db':
            if self.stats.get_value('current_page'):
                self.db_actions.update(
                    pages_crawled=self.stats.get_value('pages_crawled'),
                    current_page=self.stats.get_value('current_page'),
                    state_id=STATE_CRAWLER['Shutdown'],
                    state='Shutdown',
                    finish_time=datetime.datetime.now(),
                    finish_reason=reason)
            else:
                self.db_actions.update(
                    pages_crawled=self.stats.get_value('pages_crawled'),
                    current_page=self.stats.get_value('current_page'),
                    state_id=STATE_CRAWLER['Finished'],
                    state='Finished',
                    finish_time=datetime.datetime.now(),
                    finish_reason=reason)
    def opened(self):
        logging.info("Spider opened")
        self.add_start_info_db()

    def closed(self, reason):
        logging.info("Spider Closed")
        self.add_finish_info_db(reason)
