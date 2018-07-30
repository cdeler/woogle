from aiohttp import web
from elasticsearch import Elasticsearch


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


class Connector(object):
    def __init__(self, elastic_host, elastic_port):
        self.es = Elasticsearch()

    def curl(self, request: web.Request, method: web.Request.method):
        if method == "GET":
            index = request.query["index"]
            doc_type = request.query["doc_type"]
            search = request.query["search"]
            return self.search(index=index, doc_type=doc_type, search=search)

        elif method == "DELETE":
            index = request.query["index"]
            doc_type = request.query["doc_type"]
            doc_id = request.query["id"]
            return self.es.delete(index=index, doc_type=doc_type, id=doc_id)

        elif method == "POST":
            index = request.query["index"]
            doc_type = request.query["doc_type"]
            doc_id = request.query["id"]
            params = request.query["params"]
            return self.es.index(index=index, doc_type=doc_type, id=doc_id, params=params)

    def search(self, index, doc_type, search):
        main_search_query["query"]["simple_query_string"]["query"] = search
        response = self.es.search(index=index, doc_type=doc_type, body=main_search_query)
        return response
