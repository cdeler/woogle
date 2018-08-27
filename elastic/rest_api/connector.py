import os
import json

from elasticsearch import Elasticsearch
import elasticsearch


main_search_query = {}
DIR_PAGES = os.path.join(os.path.dirname(__file__), "config", "pages")
INDEX = "wiki"
DOC_TYPE = "page"


class Connector(object):
    def __init__(self, elastic_host, elastic_port, **kwargs):
        """

        :param elastic_host: coordinating node host
        :param elastic_port: coordinating node port
        :param kwargs: other arguments for Elasticsearch()
        """
        # we can change host_name(elasticsearch) to another,
        # but then you must change the container name to the docker-compose.yml
        self.es = Elasticsearch([{"host": elastic_host, "port": elastic_port}], **kwargs)
        self.get_main_query_from_file()
        self.delete_index()
        self.add_mapping_and_setting()
        self.add_simple_data_files()

    def curl(self, request, method):
        """
        Depending on the request method, broadcasts different requests
        :param request: user request
        :param method: request method
        :return: response object
        """
        index = request.query["index"]
        doc_type = request.query["doc_type"]

        if method == "GET":
            search = request.query["search"]
            search_mode = request.query["search_mode"]
            return self.search(index=index, doc_type=doc_type, search=search, search_mode=search_mode)

        elif method == "DELETE":
            doc_id = request.query["id"]
            return self.es.delete(index=index, doc_type=doc_type, id=doc_id)

        elif method == "POST":
            doc_id = request.query["id"]
            body = request.query["body"]
            try:
                return self.es.index(index=index, doc_type=doc_type, id=doc_id, body=body, ignore=400)
            except Exception as e:
                print(e)
                return e



    def search(self, index, doc_type, search, search_mode):
        """
        Search function
        :param index: index on es
        :param search_mode:
        :param doc_type: doc_type on es
        :param search: search phrase
        :return: response object
        """
        #  for main query
        # main_search_query["query"]["simple_query_string"]["query"] = search

        # for query with suggest
        main_search_query["suggest"]["title_suggestion"]["text"] = search
        response = self.es.search(index=index, doc_type=doc_type, body=main_search_query)
        return self.response_filter(response, search_mode)

    @staticmethod
    def response_filter(response, search_mode="normal"):
        """
        :param response:
        :param search_mode:
        :return:
        """
        response = response["suggest"]["title_suggestion"][0]["options"]
        pages = []

        tmp_dict = dict()
        for i, key in enumerate(response):
            if search_mode == "short":
                pages.append(response[i]["_source"]["title"])
            elif search_mode == "normal":
                tmp_dict = response[i]["_source"]
                tmp_dict["content"] = response[i]["_source"]["content"][:100]
                pages.append(tmp_dict)
            else:
                try:
                    pageid = int(search_mode)
                except ValueError as e:
                    print(e)
                else:
                    if response[i]["_source"].get("pageid") == pageid:
                        tmp_dict = response[i]["_source"]
                        pages.append(tmp_dict)

        rt = json.dumps(pages)
        return rt

    @staticmethod
    def get_main_query_from_file() -> None:
        """
        Reads the main search query from a file
        :return: None
        """
        global main_search_query
        with open(os.path.join(os.path.dirname(__file__), "config", "search_completion_suggester.json"), "r") as file:
            main_search_query = json.load(file)
        return main_search_query

    def __read_files__(self):
        """
        adding simple data files
        :return:
        """
        i = 0
        for root, dirs, files in os.walk(DIR_PAGES):
            for file in files:
                if file.endswith(".json"):
                    i = i + 1
                    with open(os.path.join(root, file), "r") as js_file:
                        json_obj = js_file.read()
                        self.es.index(index=INDEX, doc_type=DOC_TYPE, id=str(i), body=json_obj, ignore=400)

    def add_simple_data_files(self):
        """
        add 20 json-objects about "australia"
        :return:
        """
        try:
            self.__read_files__()
        except (FileExistsError, FileNotFoundError) as e:
            print(str(e))
        else:
            print("Successfully adding data files")

    def add_mapping_and_setting(self):
        """
        adding mapping & settings
        :return:
        """
        try:
            with open(os.path.join(os.path.dirname(__file__), "config", "es_settings.json"), "r") as file:
                setting = json.load(file)
            self.es.indices.create(index=INDEX, body=setting, ignore=400)
        except (FileExistsError, FileNotFoundError) as e:
            print(str(e))
        else:
            print("Successfully adding mapping and setting")

    def delete_index(self):
        """
        delete index
        :return:
        """
        try:

            is_index = self.es.indices.exists_alias(index=INDEX)
            if is_index:
                self.es.indices.delete(index=INDEX)
        except (elasticsearch.TransportError, elasticsearch.ConnectionError) as e:
            print(str(e))
        else:
            print("Successfully deleting")
