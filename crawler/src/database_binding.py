from src.models import Article, Meta, CrawlerStats, base
from src import WikiResponseProcessor as WikiResponseProcessor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

try:
    from scrapy.http import HtmlResponse
except Exception:
    pass
import requests
import json
import sqlalchemy.exc
import os


def init_db():
    with open(os.path.join('src', 'conf.json')) as conf:
        db_string = json.load(conf)['db_string']
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    return session


def read(session, id=None, title=None, url=None):
    if id:
        return session.query(
            Article.id,
            Article.title,
            Article.url,
            Article.text,
            Article.state).filter(
            Article.id == id).first()
    elif title:
        return session.query(
            Article.id,
            Article.title,
            Article.url,
            Article.text,
            Article.state).filter(
            Article.title == title).first()
    elif url:
        return session.query(
            Article.id,
            Article.title,
            Article.url,
            Article.text,
            Article.state).filter(
            Article.url == url).first()
    else:
        articles = session.query(Article.id, Article.title, Article.url, Article.text, Article.state)
        return articles


def get_urls_by_state(session, state="waiting"):
    urls = session.query(Article.url).filter(Article.state == state).first()
    res = [u[0] for u in urls]
    return urls[0]


def get_id_by_state(session, state="waiting"):
    ids = session.query(Article.id).filter(Article.state == state)
    res = [id[0] for id in ids]
    return res


def get_wait_url(session):
    res = session.query(Article.id, Article.url).with_for_update().filter(Article.state == "waiting").first()
    if res:
        id, url = res[0], res[1]
        update_state_by_id(session, id=id, state="...")
        return id, url
    return None


def update_state_by_id(session, id, state):
    session.query(Article).filter(Article.id == id).update(
        {'state': state}
    )
    session.commit()


def insert(session, article_info, meta_info):
    try:
        article = Article(**article_info)
        session.add(article)
        session.commit()
        session.add(Meta(article_id=article.id, meta_key='links', value=meta_info['links']))
        session.add(Meta(article_id=article.id, meta_key='page_rank', value=meta_info['page_rank']))
        session.add(Meta(article_id=article.id, meta_key='last_time_updated', value=meta_info['last_time_updated']))
        session.commit()
        return True
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        return False


def update(session, id, article_info, meta_info):
    session.query(Article).filter(Article.id == id).update(article_info)
    session.query(Meta).filter(Meta.article_id == id, Meta.meta_key == 'links').update({'value': meta_info['links']})
    session.query(Meta).filter(Meta.article_id == id, Meta.meta_key == 'page_rank').update(
        {'value': meta_info['page_rank']})
    session.query(Meta).filter(Meta.article_id == id, Meta.meta_key == 'last_time_updated').update(
        {'value': meta_info['last_time_updated']})
    session.commit()


def reparse_by_id(session, id, url):
    response = requests.get(url)
    response = HtmlResponse(url=url, body=response.content)
    WikiResponseProcessor.DBResponseProcessor().process_download(response, id_to_update=id)
    update_state_by_id(session=session, id=id, state="complete")


def delete(session, id=None, title=None, url=None):
    if id:
        session.query(Article.id).filter(Article.id == id).delete()
        session.query(Meta.article_id).filter(Meta.article_id == id).delete()
    elif title:
        session.query(Article.title).filter(Article.title == title).delete()
        id = session.query(Article.id).filter(Article.title == title).first()
        session.query(Meta.article_id).filter(Meta.article_id == id).delete()
    elif url:
        session.query(Article.url).filter(Article.url == url).delete()
        id = session.query(Article.id).filter(Article.url == url).first()
        session.query(Meta.article_id).filter(Meta.article_id == id).delete()
    else:
        session.query(Article).delete()
        session.query(Meta).delete()
        session.execute("ALTER SEQUENCE wikisearch_article_id_seq RESTART WITH 1;")
    session.commit()


def article_is_changed(session, title, last_time_updated):
    id = session.query(Article.id).filter(Article.title == title).first()
    last_time_updated_from_db = session.query(Meta.value).filter(Meta.article_id == id,
                                                                 Meta.meta_key == 'last_time_updated').first()

    # query.first() returns one value in tuple or None
    if last_time_updated_from_db:
        last_time_updated_from_db = last_time_updated_from_db[0]

    if last_time_updated == last_time_updated_from_db:
        return 0
    else:
        return 1


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
    id = session.query(Article.id).filter(Article.url == url).first()
    url = session.query(Meta.value).filter(Meta.meta_key == 'links', Meta.article_id == id)
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

    id = session.query(Article.id).filter(Article.url == url).first()
    session.query(Meta).filter(Meta.article_id == id, Meta.meta_key == 'page_rank').update({'value': pagerank})
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
