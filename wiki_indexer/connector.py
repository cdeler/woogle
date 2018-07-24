from sqlalchemy import create_engine, MetaData, Table, engine
from elasticsearch import Elasticsearch
from multiprocessing.pool import ThreadPool
import sqlalchemy


class DatabaseConnectionError(Exception):
    pass


class ElasticConnectionError(Exception):
    pass


class Connector:
    """Class that presents connector between database and
    elasticsearch.
    """
    es = Elasticsearch()

    def __init__(self, database, table,  elastic_index, elastic_doc_type):
        """
        Initialize instance.

        :param database: information about applied database.
        :type database: str.
        :param table: name of table in applied database.
        :type table: str.
        :param elastic_index: name of applied index in elasticsearch.
        :type elastic_index: str.
        :param elastic_doc_type: documents type of index of elasticsearch.
        :type elastic_doc_type: str.
        :raises :raises: TypeError, DatabaseConnectionError.
        """
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
            raise DatabaseConnectionError("Connection to databes has failed")
        self.elastic_index = elastic_index
        self.elastic_doc_type = elastic_doc_type

    @property
    def headers(self):
        """
        Method that returns name of columns/

        :returns: Tuple - headars of the table from database.
        """
        return tuple(x for x in self.table.columns)

    def get_json_from_row(self, row):
        """
        Method that unites headers of a table with a row value.

        :param row: row from table.
        :type row: sqlalchemy.engine.RowProxy.
        :returns: dict - that represent json
        :raises: TypeError, ValueError.
        """
        if not isinstance(row, tuple):
            raise TypeError("row must be tuple")
        if not isinstance(row[0], int):
            raise TypeError('first arg of row must be int')
        if row[0] < 0:
            raise ValueError('first value of row must be positive')

        return {self.headers[i].name: row[1][i] for i in range(len(self.headers))}

    @property
    def table_set(self):
        """
        Method that take all table from database as python onject.

        :returns: sqlalchemy -- table from database.
        """
        with self.engine.connect() as conn:
            select_statement = self.table.select()
            result_set = conn.execute(select_statement)
        return result_set

    def _index(self, row):
        """
        Method that put json into index in elasticsearch.

        :param row: row from table.
        :type row: sqlalchemy.engine.RowProxy.
        :return: None
        :raise: ElasticConnectionError
        """
        try:
            self.es.index(index=self.elastic_index, doc_type=self.elastic_doc_type,
                 id=row[0], body=self.get_json_from_row(row))
        except Exception as e:
            raise ElasticConnectionError("Connection to elasticsearch has failed") from e

    def index(self, threads=20):
        """
        Method that put table into index in elasticsearch in multythreading way.

        :param threads: amount of threads.
        :type threads: int.
        :returns: None.
        :raises: TypeError, ValueError.
        """
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
        """
        Method that delete all index inside elastisearch.

        :return:None.
         :raise: ElasticConnectionError
        """
        try:
            self.es.indices.delete(index=self.elastic_index, ignore=[400, 404])
        except Exception as e:
            raise ElasticConnectionError("Connection to elasticsearch has failed") from e

if __name__ == '__main__':
    con = Connector('postgresql:///test','films','test','article')
    con.delete_index()
    con.index()