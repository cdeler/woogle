from sqlalchemy import Column, INTEGER, TEXT, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Article(base):
    __tablename__ = 'articles'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(255))
    url = Column(VARCHAR(255))
    text = Column(TEXT)
    links = Column(TEXT)
    # pagerank = Column(float, default=0)


# class Meta(base):
#     __tablename__ = 'meta'
#     article_id = Column(INTEGER, ForeignKey('articles.id'), primary_key=True)
#     meta_key = Column(VARCHAR(255))
#     value = Column(VARCHAR(255))
