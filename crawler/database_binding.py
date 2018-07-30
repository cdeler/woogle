from models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_string = "postgres://username:password@localhost/dbname"
db = create_engine(db_string)

Session = sessionmaker(db)
session = Session()
base.metadata.create_all(db)


def insert(*args, **kwargs):
    session.add(Article(*args, **kwargs))
    session.commit()


def delete_all():
    session.query(Article).delete()
    session.commit()


def update():
    pass


def read():
    articles = session.query(Article)
    for article in articles:
        print(article.title)


if __name__ == '__main__':
    insert(title="some title", url="some url", text='some text')
    insert(title="some title 2", url="some url 2", text='some text 2')
    read()
    delete_all()
