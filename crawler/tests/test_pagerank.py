import sys
sys.path.append(sys.path[0] + "/..")

import unittest
import numpy as np
from unittest.mock import create_autospec

from src import pagerank


class TestPagerank(unittest.TestCase):

    def test_create_graph_positive(self):

        mock_function = create_autospec(pagerank.create_graph, return_value = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)])
        self.assertEqual(mock_function('ses'),
                         [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)])


    def test_get_probabilities(self):
        self.assertEqual(pagerank.get_probabilities(3, np.array([(0, 0, 1), (1, 1, 0), (1, 0, 0)])).tolist(),
                         [[0.0, 0.0, 1.0], [0.5, 1.0, 0.0], [0.5, 0.0, 0.0]])


    def test_pagerank(self):
        self.assertAlmostEqual(pagerank.pageRank(
            np.array([(0, 0, 0), (0, 0, 0), (0, 0, 1)])).tolist()[0], 0.0, 1)
        self.assertAlmostEqual(pagerank.pageRank(
            np.array([(0, 0, 0), (0, 0, 0), (0, 0, 1)])).tolist()[1], 0.0, 1)
        self.assertAlmostEqual(pagerank.pageRank(
            np.array([(0, 0, 0), (0, 0, 0), (0, 0, 1)])).tolist()[2], 0.0, 1)




if __name__ == '__main__':
    unittest.main()