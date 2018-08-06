from .models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.http import HtmlResponse
import requests

from .WikiResponseProcessor import *

def init_db():
    db_string = "postgresql:///test"
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    return session


def insert(session, *args, **kwargs):
    session.add(Article(*args, **kwargs))
    session.commit()


def delete_all(session):
    session.query(Article).delete()
    session.commit()


def update(session, id, title, url, text):
    session.query(Article).filter(Article.id == id).update(
        {'title': title, 'url': url, 'text': text})
    session.commit()


def reparse_by_id(session, id):
    # only for database
    url = session.query(Article.url).filter(Article.id == id).first()[0]
    response = requests.get(url)
    response = HtmlResponse(url=url, body=response.content)
    DBResponseProcessor().process(response, id_to_update=id)


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
    url = session.query(Article.urls).filter(Article.url == url)
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

def read(session):
    articles = session.query(Article)
    for article in articles:
        print(article.title)


if __name__ == '__main__':
    session = init_db()
    #insert(session, title='Sodapoppin', url='https://en.wikipedia.org/wiki/Sodapoppin',text='Thomas Jefferson Chance Morris IV (born February 15, 1994), more commonly known by his online alias Sodapoppin, a Twitch.tv streamer and former World of Warcraft player. He has among the largest following on Twitch with over 2 million followers and over 200 million views',page_rank='0')
    reparse_by_id(session, 11)
