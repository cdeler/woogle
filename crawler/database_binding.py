from models import Article, base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_db():

    db_string = "postgres://username:password@localhost/dbname"
    db = create_engine(db_string)

    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    return session


def insert(*args, **kwargs):
    session = init_db()
    session.add(Article(*args, **kwargs))
    session.commit()


def delete_all():
    session = init_db()
    session.query(Article).delete()
    session.commit()


def update():
    pass


def read():
    session = init_db()
    articles = session.query(Article)
    for article in articles:
        print(article.title)


if __name__ == '__main__':
    insert(title="some title", url="some url", text='some text')
    read()
    # delete_all()
