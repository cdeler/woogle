import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web


negative_response = """{"status": "failed", "message": "\"Key not found: 'index'\""}"""


class TestCase(AioHTTPTestCase):
    async def get_application(self):
        async def get_response(request):
            return web.Response(text=negative_response)

        app = web.Application()
        app.router.add_get('/', get_response)
        return app

    @unittest_run_loop
    async def test_nonnegative(self):
        resp = await self.client.request("GET", "/")
        assert resp.status == 200
        text = await resp.text()
        assert negative_response in text


if __name__ == '__main__':
    TestCase()
