from threading import Thread
from functools import wraps

import elasticsearch as es
from flask import jsonify

main_search_query = {
  "query": {
    "simple_query_string": {
      "query": "Australia",
      "fields": ["title^2", "content"]
    }
  },

  "size": 20,
  "_source": ["title", "pageid"],
  "sort": [{"_score": "desc"}]
}


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async_func = Thread(target=func, args=args, kwargs=kwargs)
        async_func.start()
        return async_func
    return wrapper


class Connector():
    def __init__(self, host='localhost', port=9200, **kwargs):
        if not isinstance(host, str):
            raise TypeError("host must be str")
        if not isinstance(port, int):
            raise TypeError("port must be str")

        self.elastic = es.Elasticsearch(**kwargs)

    # @run_async
    def search(self, index="_all", doc_type="_search", search=""):
        main_search_query["query"]["simple_query_string"]["query"] = search
        resp = self.elastic.search(index=index, doc_type=doc_type, body=main_search_query)
        return jsonify(resp)

    # @run_async
    def delete_doc(self, index, doc_type, id):
        response = self.elastic.delete(index=index, doc_type=doc_type, id=id)
        return jsonify(response)

    # @run_async
    def reindex(self, index, doc_type, id, params):
        responce = self.elastic.index(index=index, doc_type=doc_type, id=id, params=params)
        return jsonify(responce)
