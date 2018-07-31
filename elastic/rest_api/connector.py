import os
import json

from elasticsearch import Elasticsearch

main_search_query = {}


class Connector(object):
    def __init__(self, elastic_host, elastic_port, **kwargs):
        """

        :param elastic_host: coordinating node host
        :param elastic_port: coordinating node port
        :param kwargs: other arguments for Elasticsearch()
        """
        # we can change host_name(elasticsearch) to another,
        # but then you must change the container name to the docker-compose.yml
        self.es = Elasticsearch([{"host": 'elasticsearch'}], **kwargs)
        self.get_main_query_from_file()

    def curl(self, request, method):
        """
        Depending on the request method, broadcasts different requests
        :param request: user request
        :param method: request method
        :return: response object
        """
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
        """
        Search function
        :param index: index on es
        :param doc_type: doc_type on es
        :param search: search phrase
        :return: response object
        """
        main_search_query["query"]["simple_query_string"]["query"] = search
        response = self.es.search(index=index, doc_type=doc_type, body=main_search_query)
        return response

    def get_es(self):
        return self.es

    @staticmethod
    def get_main_query_from_file() -> None:
        """
        Reads the main search query from a file
        :return: None
        """
        global main_search_query
        with open(os.path.join(os.path.dirname(__file__), "config", "es_search.json"), "r") as file:
            main_search_query = json.load(file)
        return main_search_query
