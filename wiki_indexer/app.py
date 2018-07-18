#!flask/bin/python
from flask import Flask, abort, request
import configparser
import connector

application = Flask(__name__)
config = configparser.ConfigParser()
config.read('app.ini')


@application.route("/", methods=['POST'])
def get_tasks():
    conn = connector.Connector(config['DataBase']['dbName'],
                               config['DataBase']['dbTable'],
                               config['Elasticsearch']['index'],
                               config['Elasticsearch']['doc_type'])
    if request.data.decode('ascii') == 'index':
        conn.index()
    elif request.data.decode('ascii') == 'delete':
        conn.delete_index()
    else:
        return abort(400)
    return f'{request.data.decode("ascii")} is executed'


if __name__ == '__main__':
    application.run(threaded=True, host='0.0.0.0', port=9999)

