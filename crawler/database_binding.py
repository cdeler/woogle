from models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.http import HtmlResponse
import requests

from WikiResponseProcessor import *


def init_db():
    db_string = "postgres://username:password@localhost/dbname"
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


def update(session):
    pass


def reparse_by_id(session, id):
    # only for database
    url = session.query(Article.url).filter(Article.id == id).first()[0]
    response = requests.get(url)
    response = HtmlResponse(url=url, body=response.content)
    DBResponseProcessor().process(response)


def read(session):
    articles = session.query(Article)
    for article in articles:
        print(article.title)


if __name__ == '__main__':
    session = init_db()
    # insert(session, title="some title", url="some url", text='some text')
    reparse_by_id(session, 300)
    # read(session)
    # delete_all(session)
