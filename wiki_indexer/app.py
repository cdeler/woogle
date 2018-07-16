#!flask/bin/python
from flask import Flask, abort, request
from sqlalchemy import create_engine, MetaData, Table
import configparser
from elasticsearch import Elasticsearch
from multiprocessing.pool import ThreadPool
import logging

ROOT_LOGGER = logging.getLogger()
CONFIG = configparser.ConfigParser()
application = Flask(__name__)
es = Elasticsearch()


@application.route("/", methods=['POST'])
def get_tasks():
    """Function that get task"""
    # put articles to index
    if request.data.decode('ascii') == 'index':
        pool = ThreadPool(int(CONFIG['DEFAULT']['threadsNumber']))

        with engine.connect() as conn:
            select_statement = document.select()
            result_set = conn.execute(select_statement)

        pool.map(indexer, enumerate(result_set))

    # delete index
    elif request.data.decode('ascii') == 'delete':
        es.indices.delete(index='test', ignore=[400, 404])

    # wrong command
    else:
        return abort(400)

    return f'{request.data.decode("ascii")} is executed'


def indexer(row):
    """Function to put row from db into elasticsearch"""

    if not isinstance(row, tuple):
        raise TypeError('row must be a str')

    es.index(index=CONFIG['Elasticsearch']['index'], doc_type=CONFIG['Elasticsearch']['doc_type'],
             id=row[0], body={col[i].name: row[1][i] for i in range(len(col))})
    print(row[0])


if __name__ == '__main__':
    try:
        #get CONFIG information
        CONFIG.read('app.ini')

        #get database engine
        engine = create_engine(CONFIG['DataBase']['dbName'], echo=False)
        meta = MetaData(engine)

        #get table from database
        document = Table(CONFIG['DataBase']['dbTable'], meta, autoload=True)

        #get headers from table
        col = tuple(x for x in document.columns)

        #start application
        application.run(threaded=True, host='0.0.0.0', port=9999)

    except Exception as exc:
        #log occur exception
        ROOT_LOGGER.addHandler(logging.FileHandler('log.txt'))
        ROOT_LOGGER.exception(f'error {type(exc).__name__}: {exc.args[0]}')
