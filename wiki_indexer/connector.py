from sqlalchemy import create_engine, MetaData, Table, engine
from elasticsearch import Elasticsearch
import logging
from multiprocessing.pool import ThreadPool
import configparser
import sqlalchemy


class DatabaseConnectionError(Exception):
    pass


class ElasticConnectionError(Exception):
    pass


class Connector:
    es = Elasticsearch()
    ROOT_LOGGER = logging.getLogger()
    ROOT_LOGGER.addHandler(logging.FileHandler('log.txt'))

    def __init__(self, database, table,  elastic_index, elastic_doc_type):
        if not isinstance(database,str):
            raise TypeError("database must be str")
        if not isinstance(table,str):
            raise TypeError("table must be str")
        if not isinstance(elastic_index,str):
            raise TypeError("elastic_index must be str")
        if not isinstance(elastic_doc_type,str):
            raise TypeError("elastic_doc_type must be str")

        try:
            self.engine = create_engine(database)
            self.meta = MetaData(self.engine)
            self.table = Table(table, self.meta, autoload=True)
        except Exception as e:
            self.ROOT_LOGGER.exception(f'error {type(e).__name__}: {e.args[0]}')
            raise DatabaseConnectionError("Connection to databes has failed")
        self.elastic_index = elastic_index
        self.elastic_doc_type = elastic_doc_type

    @property
    def headers(self):
        return tuple(x for x in self.table.columns)

    def get_json_from_row(self, row):
        if not isinstance(row, tuple):
            raise TypeError("row must be tuple")
        if not isinstance(row[0], int):
            raise TypeError('first arg of row must be int')
        if row[0] < 0:
            raise ValueError('first value of row must be positive')

        return {self.headers[i].name: row[1][i] for i in range(len(self.headers))}

    @property
    def table_set(self):
        with self.engine.connect() as conn:
            select_statement = self.table.select()
            result_set = conn.execute(select_statement)
        return result_set

    def _index(self, row):
        try:
            self.es.index(index=self.elastic_index, doc_type=self.elastic_doc_type,
                 id=row[0], body=self.get_json_from_row(row))
        except Exception as e:
            self.ROOT_LOGGER.exception(f'error {type(e).__name__}: {e.args[0]}')
            raise ElasticConnectionError("Connection to elasticsearch has failed") from e

    def index(self, threads=20):
        if not isinstance(threads, int):
            raise TypeError("threads must be int")
        if threads < 0:
            raise ValueError("threads must be positive")
        if threads == 0:
            raise ValueError("number of threads must be more than 1")

        pool = ThreadPool(threads)
        pool.map(self._index, enumerate(self.table_set))
        pool.close()
        pool.join()

    def delete_index(self):
        try:
            self.es.indices.delete(index=self.elastic_index, ignore=[400, 404])
        except Exception as e:
            self.ROOT_LOGGER.exception(f'error {type(e).__name__}: {e.args[0]}')
            raise ElasticConnectionError("Connection to elasticsearch has failed") from e

if __name__ == '__main__':
    con = Connector('postgresql:///test','films','test','article')
    con.delete_index()
    con.index()