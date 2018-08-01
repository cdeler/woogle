#!flask/bin/python
from flask import Flask, abort, request
import configparser
import connector
import logging

application = Flask(__name__)
config = configparser.ConfigParser()
config.read('app.ini')
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.addHandler(logging.FileHandler('log.txt'))


@application.route("/", methods=['POST'])
def get_tasks():
    conn = connector.Connector(config['DataBase']['dbName'],
                               config['DataBase']['dbTable'],
                               config['Elasticsearch']['index'],
                               config['Elasticsearch']['doc_type'])
    try:
        if request.data.decode('ascii') == 'index':
            conn.index()
        elif request.data.decode('ascii') == 'delete':
            conn.delete_index()
        elif request.data.decode('ascii').isdigit():
            conn.index_by_id(request.data.decode('ascii'))
        else:
            return abort(400)
        return f'{request.data.decode("ascii")} is executed'
    except Exception as e:
        ROOT_LOGGER.exception(f'error {type(e).__name__}: {e.args[0]}')


if __name__ == '__main__':
    application.run(threaded=True, host='0.0.0.0', port=9999)
