import itertools
import numpy as np
from database_binding import init_db, get_urls, get_links_url, get_rows, update_page_rank
from time import time



def pageRank(M, d=0.85, squere_error=1e-6):
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

ses = init_db()


def create_graph(ses):
    """
    Function that create matrix from database.

    :param ses: session with database.
    :type sqlalchemy.session.
    :return: Graph with dependices.
    """
    names = get_urls(ses)
    x = np.zeros((3,), dtype={'names': names, 'formats': list(itertools.repeat('f4', len(names)))})
    # for i in names:
    #     links = get_links_url(ses, i)
    #     print(links)
    #     for k in links:
    #         if k in names:
    #             x[i][names.index(k)] = 1
    #     !!!!!!!!!!!!!!!!!Atempt2!!!!!!!!!!!!!!
    for i in names:
        links = set(get_links_url(ses, i))
        dependings = links & set(names)
        while dependings:
            item = dependings.pop()
            x[i][names.index(item)] = 1

    # !!!!!!!!!!!!!!!Attempt 3!!!!!!!!!!!!
    # ns = set(names)
    # namse = {i: get_links_url(ses, i) for i in names}
    # for i, j in namse.items():
    #     temp = set(j) & ns
    #     while temp:
    #         item = temp.pop()
    #         x[i][names.index(item)] = 1
    print(x)
    return x

def convert_to_array(arr):
    """
    Function that convert list of tuple array into list of lists array.

    :param arr: array that needs to be converted.
    :type arr: np.array
    :return: np.array - new
    """
    return np.asarray([list(i) for i in arr.tolist()])

def get_probabilyties(session, new_x):
    """
    Function that equally distribute probability of each vector.

    :param session: session with database.
    :type session: sqlalchemy.session.
    :param new_x: right array.
    :type new_x: np.array.
    :return: matrix.
    """
    r = get_rows(session)
    M = np.empty((r, r))
    for i in range(r):
        np.set_printoptions(precision=3)
        M[:, i] = new_x[:, i] / new_x[:, i].sum()
    print(M)
    return M


def main():
    rate = dict(zip(get_urls(ses), pageRank(get_probabilyties(ses, convert_to_array(create_graph(ses))))))
    for i, j in rate.items():
        update_page_rank(ses, i, j)

if __name__ == '__main__':

    start = time()
    result = main()
    duration = time() - start
    print(result, duration)