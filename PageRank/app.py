from __future__ import print_function
import os
import configparser

from src import database_binding as db_bind
from src.graphframes import *
from src.connector import Connector

from pyspark.sql import SQLContext
from pyspark import SparkContext
import findspark


findspark.init(os.path.join(os.path.dirname(__file__), "venv", "lib", "python3.6", "site-packages", "pyspark"))
CONFIG = configparser.ConfigParser()
CONFIG.read('app.ini')
SESSION = db_bind.init_db(CONFIG["DataBase"]["dbName"])


def get_dict_urls_from_db(session) -> list:
    """
    Set session with database(postgreSQL) and get [urls] and their links.
    Create dict-> url:[links]
    :return: dict
    """
    urls = db_bind.get_urls(session)
    dict_links = list()
    for url in urls:
        dict_links.append((url, db_bind.get_links_url(session, url)))
    return dict_links


def create_vertices_edges(session) -> ([], []):
    """

    :return:
    """
    urls = db_bind.get_url_with_id(session)
    vertices = []
    edges = []
    for u in urls:
        tmp = (str(u[0]), u[1])
        vertices.append(tmp)
        links = db_bind.get_links_url(session, u[1])
        for l in links:
            tmp = (str(u[0]), l)
            edges.append(tmp)

    return vertices, edges


if __name__ == "__main__":
    spark = SparkContext()
    sqlContext = SQLContext(spark)
    v, e = create_vertices_edges(SESSION)
    vertices = sqlContext.createDataFrame(v, ["id", "url"])

    edges = sqlContext.createDataFrame(e, ["src", "dst"])
    g = GraphFrame(v=vertices, e=edges)
    results = g.pageRank(maxIter=1).vertices
    results.show(n=500)
    for row in results.groupBy(["url", "pagerank"]).mean().collect():
        db_bind.update_page_rank(SESSION, str(row["url"]), float(row["pagerank"]))
        SESSION.commit()

    conn = Connector(CONFIG['DataBase']['dbName'],
                     CONFIG['DataBase']['dbTable'],
                     CONFIG['Elasticsearch']['index'],
                     CONFIG['Elasticsearch']['doc_type'])
    conn.index()
