import os

from elasticsearch import Elasticsearch

import service

def create_index():
    with open(os.path.join(service.DISTRO_ROOT_PATH, "config", "es_settings"), "r") as file:
        mapping = str(file.read())
    es = Elasticsearch()
    # create mapping
    es.indices.create(index="wiki", body=mapping, ignore=[500, 400])
    # adding example files
    i = 0
    for root, dirs, files in os.walk(os.path.join(service.DISTRO_ROOT_PATH, "config", "pages")):
        for file in files:
            if file.endswith(".json"):
                i = i + 1
                with open(os.path.join(root, file), "r") as file:
                    json = file.read()
                    res = es.index(index='wiki', doc_type='page', id=str(i), body=json, ignore=[500, 400])
