from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

try:
    from scrapy.http import HtmlResponse
except Exception:
    pass
import requests

from models import Article, CrawlerStats, base

DB_STRING = "postgres://postgres:password@postgres/crawler_bd"


def init_db():
    db = create_engine(DB_STRING)

    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    return session

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
