"""
Module to compute pagerank from database.
Algorithm based on 'https://en.wikipedia.org/wiki/PageRank'
"""
import itertools
import numpy as np
from crawler.database_binding import init_db, get_urls, get_links_url, get_rows, update_page_rank
import time
from functools import wraps


SQUARE_ERROR = 1e-6

def pageRank(adjacency_matrix, damping_factor=0.85, square_error=SQUARE_ERROR):
    """
    Function to get pagerank of the matrix.

    :param adjacency_matrix: matrix that represent graph of urls with dependicies.
    :type adjacency_matrix: np.array
    :param damping_factor: damping factor.
    :type damping_factor: float.
    :param square_error: difference between  two successive PageRank vectors.
    :type square_error: float.
    :returns: lists of pageranks.
    """
    n_pages = adjacency_matrix.shape[0]
    random_vect = np.random.rand(n_pages)
    random_vect = random_vect/ random_vect.sum()
    previous_vect = np.ones((n_pages))
    M_hat= damping_factor*adjacency_matrix + (1-damping_factor)/n_pages * np.ones((n_pages, n_pages))
    while np.square(random_vect - previous_vect).sum() > square_error:
        previous_vect = random_vect
        random_vect = M_hat.dot(random_vect)
    return random_vect




def create_graph(session):
    """
    Function that create matrix from database.

    :param session: session with database.
    :type session: sqlalchemy.session.
    :return: Graph with dependices.
    """
    urls = get_urls(session)
    matrix = np.zeros((len(urls),len(urls)))
    for i in urls:
        links = set(get_links_url(session, i))
        dependings = links & set(urls)
        if not dependings :
            for j in range(len(matrix[urls.index(i)])):
                matrix[urls.index(i)] = 1
        while dependings:
            item = dependings.pop()
            matrix[urls.index(i)][urls.index(item)] = 1
    print(matrix)
    return matrix.transpose()

print(create_graph(init_db()))



def get_probabilyties(rows, matrix):
    """
    Function that equally distribute probability of each vector.

    :param rows: amount of rows in matrix.
    :type rows: int.
    :param matrix: right array.
    :type matrix: np.array.
    :return: matrix.
    """
    blank_matrix = np.empty((rows, rows))
    for i in range(rows):
        np.set_printoptions(precision=3)
        blank_matrix[:, i] = matrix[:, i] / matrix[:, i].sum()
    return blank_matrix


def _test_working_time(debug=False):
    """
    Decorator to measure the running time
    :param debug: status of running program.
    :return: inner function.
    """
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if debug:
                started_time = time.time()
                result = func(*args, **kwargs)
                print(time.time() - started_time)
            else:
                result = func(*args, **kwargs)
            return result
        return inner
    return decorator


@_test_working_time()
def compute_pagerank():
    """
    Compute pagerank

    :returns bool - true if computed successfully, false if computation failed.
    """
    session = init_db()
    success = True
    try:
        rate = dict(zip(get_urls(session),
                        pageRank(
                            get_probabilyties(get_rows(session),
                            create_graph(session))
                        )))
        for i, j in rate.items():
            update_page_rank(session, i, j)
    except Exception:
        success = False
    finally:
        session.commit()
    return success




