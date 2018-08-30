"""
Runs  crawler (WikiSpider) and downloader
"""
import argparse
import logging
import concurrent.futures
import multiprocessing

from src.WikiSpider import get_process
from src import setting_language as setting
from src.WikiSpider import WikiSpider
from src.PidFile import PidFile
from src import downloader

MAX_COUNT_THREADS = 10
CHOICE_LANGUAGE = list(setting.LANGUAGE_SETTING.keys())  # ['ru', 'en']
CHOICE_OUTPUT = ['db', 'stdout','directory']
LOG_LEVEL = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

def multiprocess(count_workers: int, args):
    """
    Runs WikiSpider in one process and runs in count_workers-1 processes the downloader
    :param count_workers: count processes
    :type count_workers: int
    :param args: argument for crawler
    :type args: dict
    :return: None
    """
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
    """
    Runs crawler with arguments
    :param args: arguments for crawler
    :type args: dict
    :return: None
    """
    with PidFile(name=args['pidfile']):
        logging.info(f"Crawler starts with options: {args}")
        process = get_process(args['logfile'],args['loglevel'])
        process.crawl(WikiSpider, args['language'],args['output'],args['silent'])
        process.start()  # the script will block here until the crawling is finished

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Run wiki-downloader&parser with given options.',
    epilog='File with spider MUST be in the same directory as this file. \
                The logic of processing arguments is inside called spider. \
                Arguments just define its behaviour depending on their values.')

    # define optional arguments
    parser.add_argument('-l',
        '--language',
        help=f'wikipedia language (default: {CHOICE_LANGUAGE[0]})',
        type=str,
        choices=CHOICE_LANGUAGE,
        default=CHOICE_LANGUAGE[0])
    parser.add_argument(
        '-o',
        '--output',
        help=f'output (default: {CHOICE_OUTPUT[0]})',
        type=str,
        choices=CHOICE_OUTPUT,
        default=CHOICE_OUTPUT[0])
    arg_s = parser.add_argument(
        '-s',
        '--silent',
        help='turn on silent mode, use with output=stdout (default: False)',
        action='store_true')
    parser.add_argument(
        '--logfile',
        help='log file. if omitted stderr will be used',
        type=str,
        metavar="FILE",
        default=None)
    parser.add_argument(
        '--loglevel',
        help='log level (default: DEBUG)',
        choices=LOG_LEVEL,
        default='DEBUG')
    parser.add_argument(
        "--pidfile",
        type=str,
        metavar="FILE",
        help="run scrapy with pidfile = FILE (default: pidfile)",
        default='pidfile')
    parser.add_argument(
        "--jobdir",
        type=str,
        metavar="FILE",
        help="pausing and resuming crawler",
        default=None)
    parser.add_argument("-c", "--concurrency", type=int, default=multiprocessing.cpu_count(),
                        help="specify the concurrency (for debugging and timing) [default: %(default)d]")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="database host")

    arg = vars(parser.parse_args())

    if arg['silent'] and arg['output'] != 'stdout':
        msg = "isn't used with argument -o|--output equal 'stdout'"
        raise argparse.ArgumentError(arg_s, msg)

    # database_binding.DB_STRING.replace("localhost", arg["host"])

    multiprocess(count_workers=arg["concurrency"], args=arg)
