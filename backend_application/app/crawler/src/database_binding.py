from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

try:
    from scrapy.http import HtmlResponse
except Exception:
    pass
import requests

from src.models import Article, CrawlerStats, base
from src import WikiResponseProcessor


def init_db():
    db_string = "postgres://postgres:password@localhost/crawler_bd"
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    return session


def read(session, id=None, title=None, url=None):
    if id:
        return session.query(
            Article.title,
            Article.url,
            Article.text).filter(
            Article.id == id).first()
    elif title:
        return session.query(
            Article.title,
            Article.url,
            Article.text).filter(
            Article.title == title).first()
    elif url:
        return session.query(
            Article.title,
            Article.url,
            Article.text).filter(
            Article.url == url).first()
    else:
        articles = session.query(Article.title, Article.url, Article.text)
        return articles


def insert(session, *args, **kwargs):
    session.add(Article(*args, **kwargs))
    session.commit()


def update(session, id, title, url, text, links):
    session.query(Article).filter(Article.id == id).update(
        {'title': title, 'url': url, 'text': text, 'links': links})
    session.commit()


def reparse_by_id(session, id):
    url = session.query(Article.url).filter(Article.id == id).first()[0]
    response = requests.get(url)
    response = HtmlResponse(url=url, body=response.content)
    WikiResponseProcessor.DBResponseProcessor().process(response, id_to_update=id)


def delete(session, id=None, title=None, url=None):
    if id:
        session.query(Article.id).filter(Article.id == id).delete()
    elif title:
        session.query(Article.title).filter(Article.title == title).delete()
    elif url:
        session.query(Article.url).filter(Article.url == url).delete()
    else:
        session.query(Article).delete()
    session.commit()


def get_rows(ses):
    """
    Function to get amount of rows in a table.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session
    :returns: integer amount of rows in table
    """
    return ses.query(Article).count()


def get_urls(session):
    """
    Function to get all urls of article in a table.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session
    :returns: integer amount of rows in table
    """
    url = session.query(Article.url)
    res = [u[0] for u in url]
    return res


def get_links_url(session, url):
    """
    Function to get all urls that referred on other article.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session.
    :param url: url of article with dependicies.
    :type url: str.
    :returns: list of strings - list of urls
    """
    url = session.query(Article.links).filter(Article.url == url)
    return [u[0].split() for u in url][0]


def update_page_rank(session, url, pagerank):
    """
    Function to update page rank by id.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session.
    :param url: url of article.
    :type url: str.
    :param pagerank: new pagerank for artiocle.
    :type pagerank: float
    :returns: None
    """
    url = session.query(Article.page_rank).filter(Article.url == url).update({
        'page_rank': pagerank
    })
    session.commit()


class CrawlerStatsActions():
    """
    class for actions with a table "CrawlerStats"
    """

    def create(self, *args, **kwargs):
        """
        Create row in table "CrawlerStats" for crawler
        :param args:
        :param kwargs:
        :return:
        """
        self.session = init_db()
        self.instance = CrawlerStats(*args, **kwargs)
        self.session.add(self.instance)
        self.session.commit()

    def update(self, *args, **kwargs):
        """
        Update row in table "CrawlerStats" for crawler
        :param args:
        :param kwargs:
        :return:
        """
        if 'pages_crawled' in kwargs:
            self.instance.pages_crawled = kwargs['pages_crawled']
        if 'current_page' in kwargs:
            self.instance.current_page = kwargs['current_page']
        if 'state_id' in kwargs:
            self.instance.state_id = kwargs['state_id']
        if 'state' in kwargs:
            self.instance.state = kwargs['state']
        if 'finish_time' in kwargs:
            self.instance.finish_time = kwargs['finish_time']
        if 'finish_reason' in kwargs:
            self.instance.finish_reason = kwargs['finish_reason']

        self.session.commit()

    @staticmethod
    def get_shutdown_crawler(language, state_id):
        """Returns instance of class CrawlerStatsActions with crawler that has a state_id ('shutdown') and language
        """
        CrawlerStatsActions.refresh_crawlers()
        session = init_db()
        stats_crawlers = session.query(CrawlerStats).filter_by(
            language=language, state_id=state_id).all()
        if len(stats_crawlers) != 0:
            if len(stats_crawlers) != 1:
                logging.warning(
                    "Warning: there are many crawlers with the state 'shutdown'. Selected the first ")
            bd_actions = CrawlerStatsActions()
            bd_actions.session = session
            bd_actions.instance = stats_crawlers[0]
            return bd_actions
        else:
            return None

    @staticmethod
    def refresh_crawlers():
        """
        Refresh state of all crawler from 'working' to 'shutdown'
        :return:
        """
        session = init_db()
        crawlers = session.query(CrawlerStats).filter_by(state_id=1).all()
        for c in crawlers:
            c.state = 'Shutdown'
            c.state_id = 2
        session.commit()
