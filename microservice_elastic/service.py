#!/usr/bin/env python3

import os
import datetime
import argparse
import configparser
import logging
import json

import asyncio
from aiohttp import web

from connector import Connector

CONNECTOR = Connector
ROOT_LOGGER = logging.getLogger()
CONFIG = configparser.ConfigParser()
DISTRO_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
default_elastic_host = "127.0.0.1"
default_elastic_port = 9200


@asyncio.coroutine
def porter(request: web.Request):
    """
    автоматически транслировать все запросы проходящие
    :param request:
    :return:
    """
    try:
        # try get response
        response_obj = CONNECTOR.curl(request, request.method)
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as error:
        response_obj = {"status": "failed", "message": str(error)}
        return web.Response(text=json.dumps(response_obj), status=500)


@asyncio.coroutine
def init(loop, address, port):
    app = web.Application()
    app.add_routes([web.get("/", porter)])
    handler = app._make_handler()
    server = yield from loop.create_server(handler, address, port)
    return server.sockets[0].getsockname()


def run_server(address, port):
    loop = asyncio.get_event_loop()
    host = loop.run_until_complete(init(loop, address, port))
    debug_output("Serving on {}. Hit CTRL-C to stop.".format(host))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    debug_output("\nServer shutting down.")
    loop.close()


def debug_output(text_message: str):
    ROOT_LOGGER.info(text_message)
    print(text_message)


if __name__ == '__main__':
    try:
        CONFIG.read("config_service.ini")
        default_elastic_host = CONFIG.get("elasticsearch", "host")
        default_elastic_port = CONFIG.get("elasticsearch", "port")
    except configparser.Error as e:
        debug_output(str(e))

    CONNECTOR = Connector(default_elastic_host, default_elastic_port)

    parser = argparse.ArgumentParser(description="http server for elasticsearch")
    parser.add_argument("--host", type=str, help="specify the required host", default="127.0.0.1")
    parser.add_argument("--port", type=int, help="specify the required port", default=5000)
    parser.add_argument("--verbose", help="enable debug mode", action="store_true")
    args = parser.parse_args()

    # configuration logger
    if args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.ERROR

    ROOT_LOGGER.setLevel(log_level)
    ROOT_LOGGER.addHandler(logging.FileHandler(os.path.join(DISTRO_ROOT_PATH, 'logs', 'log.txt')))
    ROOT_LOGGER.info("\nBeginning at: {}".format(datetime.datetime.now()))

    # starting server
    run_server(address=args.host, port=args.port)
