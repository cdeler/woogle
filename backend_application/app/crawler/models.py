from sqlalchemy import Column, INTEGER, TEXT, VARCHAR, FLOAT, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Article(base):
    __tablename__ = 'wikisearch_article'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(255))
    url = Column(VARCHAR(1000))
    text = Column(TEXT)
    links = Column(TEXT)
    page_rank = Column(FLOAT, default=0)


# class Meta(base):
#     __tablename__ = 'meta'
#     article_id = Column(INTEGER, ForeignKey('articles.id'), primary_key=True)
#     meta_key = Column(VARCHAR(255))
#     value = Column(VARCHAR(255))
