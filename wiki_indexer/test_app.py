import unittest
import requests

class TestApp(unittest.TestCase):


    def test_post_delete(self):
        response = requests.post( 'http://0.0.0.0:9999/', 'delete')
        self.assertEqual(response.text,'delete is executed')

    def test_post_index(self):
        response = requests.post('http://0.0.0.0:9999/', 'index')
        self.assertEqual(response.text, 'index is executed')

    def test_post_some_wrong_request(self):
        response = requests.post('http://0.0.0.0:9999/', 'something')
        self.assertEqual(response.text,
                         '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
                         '<title>400 Bad Request</title>\n'
                         '<h1>Bad Request</h1>\n'
                         '<p>The browser (or proxy) sent a request that this server could not understand.</p>\n')

if __name__ == '__main__':
    unittest.main()