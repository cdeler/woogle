from crawler.src.models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from scrapy.http import HtmlResponse
except Exception:
    pass
import requests

from crawler.src import WikiResponseProcessor


def init_db():
    db_string = "postgres://username:password@localhost/dbname"
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
        session.execute("ALTER SEQUENCE wikisearch_article_id_seq RESTART WITH 1;")
    session.commit()

def get_rows(session):
    """
    Function to get amount of rows in a table.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session
    :returns: integer amount of rows in table
    """
    return session.query(Article).count()



def get_urls(session):
    """
    Function to get all urls of article in a table.

    :param session: session establishes all conversations with the database and represents a “holding zone”.
    :type session: sqlalchemy.session
    :returns: integer amount of rows in table
    """
    url = session.query(Article.url)
    return [u[0] for u in url]



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


