import argparse
import functools
import logging
import concurrent.futures
import multiprocessing

from src import setting_language as setting
from src.WikiSpider import process
from src.WikiSpider import WikiSpider
from src.PidFile import PidFile
from src import downloader
from src import database_binding

MAX_COUNT_THREADS = 10
CHOICE_LANGUAGE = list(setting.LANGUAGE_SETTING.keys())  # ['ru', 'en']
CHOICE_OUTPUT = ['stdout', 'db', 'directory']


def args2dict(args):
    """
    Transform string with arguments into dictionary with them.

    :param args: input string.
    :return: dictionary with parsed arguments
    """
    arg_dict = {}
    for argument in args:
        key, value = argument.split('=')
        if value.startswith('\\'):
            arg_dict[key] = value[1:]
        else:
            arg_dict[key] = value
    return arg_dict


def multiprocess(count_workers: int, args):
    futures = set()
    with concurrent.futures.ProcessPoolExecutor(max_workers=count_workers) as executor:
        future = executor.submit(fn=wiki_spider, args=args)
        futures.add(future)
        for i in range(count_workers-1):
            future_d = executor.submit(fn=downloader.start_download)
            # future_d.add_done_callback(finished_downloader)

            futures.add(future_d)
        executor.shutdown(wait=False)



def wiki_spider(args):
    with PidFile():
        logging.info("Start crawler")
        process.crawl(WikiSpider, arg=args)
        process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run wiki-downloader&parser with given options.',
        epilog='File with spider MUST be in the same directory as this file. \
                The logic of processing arguments is inside called spider. \
                Arguments just define its behaviour depending on their values.')

    # define optional arguments
    parser.add_argument('-n', '--num-threads', help='count threads (defalut: 1)', type=int,
                        choices=range(1, MAX_COUNT_THREADS), default='1')
    parser.add_argument('-l', '--language', help=f'wikipedia language (default: {CHOICE_LANGUAGE[1]})', type=str,
                        choices=CHOICE_LANGUAGE, default=CHOICE_LANGUAGE[1])
    parser.add_argument('-o', '--output', help=f'output (default: {CHOICE_OUTPUT[1]})', type=str, choices=CHOICE_OUTPUT,
                        default=CHOICE_OUTPUT[0])
    parser.add_argument("-c", "--concurrency", type=int, default=multiprocessing.cpu_count(),
                        help="specify the concurrency (for debugging and timing) [default: %(default)d]")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="database host")
    arg_s = parser.add_argument('-s', '--silent', help='turn on silent mode, use with output=stdout (default: False)',
                                action='store_true')

    arg = vars(parser.parse_args())
    if arg['silent'] and arg['output'] != 'stdout':
        msg = "isn't used with argument -o|--output equal 'stdout'"
        raise argparse.ArgumentError(arg_s, msg)

    database_binding.DB_STRING.replace("localhost", arg["host"])

    arguments_for_crawler = functools.reduce(lambda x, y: x + y, [f"{key}={value} " for key, value in arg.items()], "")
    logging.info(f"Crawler starts with options: {arguments_for_crawler}")

    multiprocess(count_workers=arg["concurrency"], args=arguments_for_crawler)
