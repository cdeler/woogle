#!flask/bin/python
from flask import Flask, abort, request
import configparser
import connector
from pagerank import compute_pagerank


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
        print("Pagarank is calculating...")
        compute_pagerank()
        print("Pass data to elasticsearch.")
        conn.index()
    elif request.data.decode('ascii').isdigit():
        conn.index(request.data.decode('ascii'))
    else:
        return abort(400)
    return f'{request.data.decode("ascii")} is executed'


if __name__ == '__main__':
    application.run(threaded=True, host='0.0.0.0', port=9999)