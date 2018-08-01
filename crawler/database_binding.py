from models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.http import HtmlResponse
import requests

from WikiResponseProcessor import DBResponseProcessor


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


def update(session, id, title, url, text):
    session.query(Article).filter(Article.id == id).update(
        {'title': title, 'url': url, 'text': text})
    session.commit()


def reparse_by_id(session, id):
    url = session.query(Article.url).filter(Article.id == id).first()[0]
    response = requests.get(url)
    response = HtmlResponse(url=url, body=response.content)
    DBResponseProcessor().process(response, id_to_update=id)


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


if __name__ == '__main__':
    session = init_db()
    # dict = {'title':"some title", 'url':"some url", 'text':'some text'}
    # insert(session, **dict)
    # columns = ('title', 'url', 'text')
    # input_data = ('some title', 'some url', 'some text')
    # input_row = {k: v for k, v in zip(columns, input_data)}
    # id = 500
    # insert(session, id=id, **input_row)
    # insert(session, title="some title", url="some url", text='some text')
    reparse_by_id(session, 345)
    # print(read(session, title='some title'))
    # print(read(session, id=5))
    # delete(session, id=349)
