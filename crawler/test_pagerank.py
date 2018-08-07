import unittest
import numpy as np
from unittest.mock import patch
import pagerank
import sys


class ImportBlocker(object):
    def __init__(self, *args):
        self.module_names = args

    def find_module(self, fullname, path=None):
        if fullname in self.module_names:
            return self
        return None

    def exec_module(self, mdl):
        # return an empty namespace
        return {}

sys.meta_path=[ImportBlocker('scrapy.http')]


class TestPagerank(unittest.TestCase):

    def test_create_graph_positive(self):
        with patch('pagerank.init_db'), patch('pagerank.get_urls') as mocked_urls:
            mocked_urls.return_value = ['Andrei','Nikita','Sergei']
            with patch('pagerank.get_links_url') as scammed_urls:
                scammed_urls.return_value = ['Nikita','Nikita']
                ses = pagerank.init_db()
                self.assertEqual(pagerank.create_graph(ses).tolist() ,[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)])


    def test_get_probabilyties(self):
        with patch('pagerank.init_db'),patch('pagerank.get_rows') as scammed_rows:
            scammed_rows.return_value = 3
            ses = pagerank.init_db()

            self.assertEqual(pagerank.get_probabilyties(ses,np.array([(0,0,1),(1,1,0),(1,0,0)])).tolist(),
                             [[0.0, 0.0, 1.0], [0.5, 1.0, 0.0], [0.5, 0.0, 0.0]])

    def test_pagerank(self):
        self.assertAlmostEqual(pagerank.pageRank(np.array([(0,0,0),(0,0,0),(0,0,1)])).tolist()[0],0.0,1)
        self.assertAlmostEqual(pagerank.pageRank(np.array([(0, 0, 0), (0, 0, 0), (0, 0, 1)])).tolist()[1], 0.0, 1)
        self.assertAlmostEqual(pagerank.pageRank(np.array([(0, 0, 0), (0, 0, 0), (0, 0, 1)])).tolist()[2], 0.0, 1)

    def test_convert_to_array(self):
        x = np.zeros(2, dtype={'names':['a','v'], 'formats': ['f4','f4']})
        self.assertEqual(pagerank.convert_to_array(x).tolist(),[[0., 0.],[0., 0.]])

if __name__ == '__main__':
    unittest.main()