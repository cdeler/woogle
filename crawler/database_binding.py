from models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.http import HtmlResponse
import requests

import WikiResponseProcessor


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
    session.commit()