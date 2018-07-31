import unittest
from connector import Connector

class TestApp(unittest.TestCase):
    conn = Connector("127.0.0.1", 5000)
    def test_connector_index_request(self):
        response_obj = self.conn.search(index="wiki", doc_type="page", search="Australia")
        self.assertEqual(len(response_obj), 4)



if __name__ == '__main__':
    unittest.main()