from sqlalchemy import Column, INTEGER, TEXT, VARCHAR, FLOAT, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Article(base):
    __tablename__ = 'wikisearch_article'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(TEXT)
    url = Column(TEXT, unique=True)
    text = Column(TEXT)
    links = Column(TEXT)
    page_rank = Column(FLOAT, default=0)
    state = Column(VARCHAR(20), default="waiting")


# class Meta(base):
#     __tablename__ = 'meta'
#     article_id = Column(INTEGER, ForeignKey('articles.id'), primary_key=True)
#     meta_key = Column(VARCHAR(255))
#     value = Column(VARCHAR(255))


class CrawlerStats(base):
    __tablename__ = 'crawler_stats'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    start_time = Column(TIMESTAMP)
    language = Column(VARCHAR(2))
    pages_crawled = Column(INTEGER)
    current_page = Column(TEXT)
    state_id = Column(INTEGER)
    state = Column(VARCHAR(50))  # working, finish
    finish_time = Column(TIMESTAMP, nullable=True)
    finish_reason = Column(VARCHAR(50), nullable=True)
