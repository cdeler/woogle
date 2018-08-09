#!/usr/bin/env python3

import os
import datetime
import argparse
import logging
import json

import asyncio
from aiohttp import web

from connector import Connector
import configs


CONNECTOR = Connector
ROOT_LOGGER = logging.getLogger()
DISTRO_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


@asyncio.coroutine
def porter(request: web.Request):
    """
    Function as an intermediary between the ElasticSearchEngine and the user.
    Translates all user requests into an ElasticSearch
    :param request: user request
    :type request: web.Request
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
def init(loop, host, port):
    """
    Initializing a web application, setting routes
    :param loop:
    :type loop: asyncio event loop
    :param host: rest_api host
    :type host: str
    :param port: rest_api port
    :type port: int
    :return:
    """
    app = web.Application()
    app.add_routes([web.get("/", porter)])
    handler = app._make_handler()
    server = yield from loop.create_server(handler, host, port)
    return server.sockets[0].getsockname()


def run_server(host: str, port: int):
    """
    Сonditional server startup. A loop is created for asynchronous query processing
    :param host: rest_api host
    :type host: str
    :param port: rest_api port
    :type port: int
    :return:
    """
    loop = asyncio.get_event_loop()
    runtime = loop.run_until_complete(init(loop, host, port))
    debug_output("Serving on {}. Hit CTRL-C to stop.".format(runtime))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    debug_output("\nServer shutting down.")
    loop.close()


def debug_output(text_message: str):
    """
    Output to the console and the log file
    :param text_message:
    :return: None
    """
    ROOT_LOGGER.info(text_message)
    print(text_message)


def waiting_connection_with_es(elastic_host: str, elastic_port: int):
    """
    We are waiting for connection to elasticsearch
    At initialization, the dead_timeout attribute is passed, which pauses and repeats again
    :return: None
    """
    global CONNECTOR
    CONNECTOR = Connector(elastic_host, elastic_port, dead_timeout=20)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="http server for elasticsearch")
    parser.add_argument(
        "--verbose",
        help="enable debug mode",
        action="store_true")
    parser.add_argument(
        "--mapping",
        type=bool,
        help="create index with mapping and setting up es",
        default=False)
    parser.add_argument(
        "--delete",
        type=bool,
        help="delete data and index",
        default=False)
    parser.add_argument(
        "--data",
        type=bool,
        help="add simple data_files in ES",
        default=False)
    args = parser.parse_args()

    # read the configuration settings
    conf = configs.Config()

    # waiting connection
    waiting_connection_with_es(conf.elastic_host, conf.elastic_port)

    # configuration logger
    if args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.ERROR

    ROOT_LOGGER.setLevel(log_level)
    ROOT_LOGGER.addHandler(
        logging.FileHandler(
            os.path.join(
                DISTRO_ROOT_PATH,
                'logs',
                'log.txt')))
    ROOT_LOGGER.info("\nBeginning at: {}".format(datetime.datetime.now()))

    # starting
    run_server(host=conf.api_host, port=conf.api_port)
