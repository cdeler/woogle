import itertools
import numpy as np
from crawler.database_binding import init_db, get_urls, get_links_url, get_rows, update_page_rank
import time


SQUERE_ERROR = 1e-6

def pageRank(M, d=0.85, squere_error=SQUERE_ERROR):
    """
    Function to get pagerank of the matrix.

    :param M: matrix that represent graph of urls with dependicies.
    :type M: np.array
    :param d: damping factor.
    :type d: float.
    :param squere_error: difference between  two successive PageRank vectors.
    :type squere_error: float.
    :returns: lists of pageranks.
    """
    n_pages = M.shape[0]
    v = np.random.rand(n_pages)

    v = v/ v.sum()

    last_v = np.ones((n_pages))
    M_hat =  d*M + (1-d)/n_pages * np.ones((n_pages, n_pages))
    while np.square(v - last_v).sum() > squere_error:
        last_v = v
        v = M_hat.dot(v)
    return v




def create_graph(ses):
    """
    Function that create matrix from database.

    :param ses: session with database.
    :type sqlalchemy.session.
    :return: Graph with dependices.
    """
    names = get_urls(ses)
    x = np.zeros((len(names),), dtype={'names': names, 'formats': list(itertools.repeat('f4', len(names)))})

    for i in names:
        links = set(get_links_url(ses, i))
        dependings = links & set(names)
        if not dependings :

            for j in range(len(x[i])):

                x[i][j] = 1
        while dependings:
            item = dependings.pop()
            x[i][names.index(item)] = 1

    return x

def convert_to_array(arr):
    """
    Function that convert list of tuple array into list of lists array.

    :param arr: array that needs to be converted.
    :type arr: np.array
    :return: np.array - new
    """
    return np.asarray([list(i) for i in arr.tolist()])

def get_probabilyties(rows, new_x):
    """
    Function that equally distribute probability of each vector.

    :param session: session with database.
    :type session: sqlalchemy.session.
    :param new_x: right array.
    :type new_x: np.array.
    :return: matrix.
    """
    r = rows
    M = np.empty((r, r))
    for i in range(r):
        np.set_printoptions(precision=3)
        M[:, i] = new_x[:, i] / new_x[:, i].sum()
    return M

def compute_pagerank():
    """
    Compute pagerank
    """
    t1 = time.time()
    success = True
    try:
        ses = init_db()
        rate = dict(zip(get_urls(ses), pageRank(get_probabilyties(get_rows(ses), convert_to_array(create_graph(ses))))))
        for i, j in rate.items():
            update_page_rank(ses, i, j)
    except Exception as e:
        success = False
        print(f'error {type(e).__name__}: {e.args[0]}')
    print(t1 - time.time())
    return success
