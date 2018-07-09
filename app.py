#!flask/bin/python
from flask import Flask, jsonify
from flask import abort

application = Flask(__name__)

@application.route("/<string:ping>", methods=["GET"])
def get_tasks(ping):
    return "pong" if ping == "ping" else abort(404) #jsonify({'pong': "0"})

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80)
