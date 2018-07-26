from flask import Flask

from connector import Connector

application = Flask(__name__)
connector = Connector()


@application.route("/<string:index>/<string:doc_type>/<string:search>", methods=["GET"])
def search(index, doc_type, search):
    return connector.search(index=index, doc_type=doc_type, search=search)


@application.route("/<string:index>/<string:doc_type>/<int:id>/<string:params>", methods=["POST"])
def reindex(index, doc_type, id, params):
    return connector.reindex(index=index, doc_type=doc_type, id=id, params=params)


@application.route("/<string:index>/<string:doc_type>/<int:id>", methods=["DELETE"])
def delete_doc(index, doc_type, id):
    return connector.delete_doc(index=index, doc_type=doc_type, id=id)


if __name__ == "__main__":
    application.run(threaded=True)
