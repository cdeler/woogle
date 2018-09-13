from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Article, base


def init_db(db_string):
    """

    :return:
    """
    db = create_engine(db_string)
    session_maker = sessionmaker(db)
    session = session_maker()
    base.metadata.create_all(db)
    return session


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
    session.query(Article.page_rank).filter(Article.url == url).update({
        'page_rank': pagerank
    })


def get_table(session):
    """
    get all rows from database
    :param session:
    :return:
    """
    table = session.query(Article.id, Article.url, Article.links, Article.page_rank).filter(Article.state == "Complete")
    return table


def get_url_with_id(session):
    """
    get all id and url from table
    :param session:
    :return:
    """
    url = session.query(Article.id, Article.url)
    res = [u for u in url]
    return res
