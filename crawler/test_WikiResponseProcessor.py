import unittest
import requests
import shutil
import os
try:
    from scrapy.http import HtmlResponse
except Exception as e:
    pass
import WikiResponseProcessor
import io
from contextlib import redirect_stdout


class TestParsers(unittest.TestCase):

    def test_same_out(self):
        expected_result = "Ру́сский язы́к ([ˈruskʲɪi̯ jɪˈzɨk]"

        url = "https://ru.wikipedia.org/wiki/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA"

        response = requests.get(url)
        response = HtmlResponse(url=url, body=response.content)

        f = io.StringIO()
        with redirect_stdout(f):
            WikiResponseProcessor.StdOutWikiResponseProcessor().process(response, 20)
        result1 = f.getvalue()

        additional = len(f'\n------\n\n {response.url} \n')

        self.assertSequenceEqual(result1[additional:20+additional], expected_result[:20])

    def test_same_parsed(self):
        url = "https://ru.wikipedia.org/wiki/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA"

        response = requests.get(url)
        response = HtmlResponse(url=url, body=response.content)

        f = io.StringIO()
        with redirect_stdout(f):
            WikiResponseProcessor.StdOutWikiResponseProcessor().process(response, 150)
        result1 = f.getvalue()

        cur_path = os.getcwd()
        os.chdir(cur_path)
        os.mkdir('temp')
        path = os.path.join(cur_path, 'temp')
        WikiResponseProcessor.FileWikiResponseProcessor().process(response, path)
        file = os.listdir('temp')[0]
        with open(os.path.join(path, file)) as input:
            resf = input.readline()

        shutil.rmtree(cur_path)
        additional = len(f'\n------\n\n {response.url} \n')

        self.assertSequenceEqual(result1[additional:additional+150], resf[:150])


if __name__ == '__main__':
    unittest.main()