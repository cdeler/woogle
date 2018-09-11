from pyspark.sql import SQLContext
from pyspark import SparkContext

from graphframes import *


if __name__ == '__main__':
    spark = SparkContext.getOrCreate()
    sqlContext = SQLContext(spark)

    vertices = sqlContext.createDataFrame([
        ("a", "temp_url_1"),
        ("b", "temp_url_2"),
        ("c", "temp_url_3"),
        ("d", "temp_url_4"),
        ("e", "temp_url_5"),
        ("f", "temp_url_6"),
        ("g", "temp_url_7")], ["id", "url"])

    edges = sqlContext.createDataFrame([
        ("a", "b"),
        ("b", "c"),
        ("c", "b"),
        ("f", "c"),
        ("e", "f"),
        ("e", "d"),
        ("d", "a"),
        ("a", "e")
    ], ["src", "dst"])

    g = GraphFrame(v=vertices, e=edges)
    g.inDegrees.show(truncate=False)

    results = g.pageRank(maxIter=20)

