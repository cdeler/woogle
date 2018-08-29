from sqlalchemy import Column, INTEGER, TEXT, VARCHAR, FLOAT, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Article(base):
    __tablename__ = 'wikisearch_article'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(TEXT)
    url = Column(TEXT)
    text = Column(TEXT)
    state = Column(VARCHAR(20), default="waiting")
    page_rank = Column(FLOAT, default=0)
    last_time_updated = Column(VARCHAR(1024))

class Links(base):
    __tablename__ = 'links'
    article_id = Column(INTEGER, ForeignKey('wikisearch_article.id'), primary_key=True)
    link_article_id = Column(INTEGER, ForeignKey('wikisearch_article.id'), primary_key=True)
    __table_args__ = (UniqueConstraint('article_id', 'link_article_id', name='_article_link_uc'),)

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
