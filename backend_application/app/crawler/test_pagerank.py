import unittest
import numpy as np
from unittest.mock import patch, Mock, create_autospec

from crawler import pagerank

class TestPagerank(unittest.TestCase):

    def test_create_graph_positive(self):
        with patch('pagerank.get_urls') as mocked_urls:
            mocked_urls.return_value = ['Andrei','Nikita','Sergei']
            with patch('pagerank.get_links_url') as scammed_urls:
                scammed_urls.return_value = ['Nikita','Nikita']
                mock_function = create_autospec(pagerank.create_graph, return_value = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)])
                self.assertEqual(mock_function('ses'),
                                 [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)])


    def test_get_probabilyties(self):
        self.assertEqual(pagerank.get_probabilyties(3,np.array([(0,0,1),(1,1,0),(1,0,0)])).tolist(),
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