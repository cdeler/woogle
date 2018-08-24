import argparse
import functools
import logging



from src.WikiSpider import get_process
import concurrent.futures
import multiprocessing

from src import setting_language as setting

from src.WikiSpider import WikiSpider
from src.PidFile import PidFile
from src import downloader
from src import database_binding

MAX_COUNT_THREADS = 10
CHOICE_LANGUAGE = list(setting.LANGUAGE_SETTING.keys())  # ['ru', 'en']
CHOICE_OUTPUT = ['stdout', 'db', 'directory']
LOG_LEVEL = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

arg_dict=0
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
        logging.info("Start crawler.")
        process = get_process(arg_dict['logfile'], arg_dict['loglevel'], arg_dict['jobdir'])
        process.crawl(WikiSpider, arg=args)
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
    arg_dict=arg
    if arg['silent'] and arg['output'] != 'stdout':
        msg = "isn't used with argument -o|--output equal 'stdout'"
        raise argparse.ArgumentError(arg_s, msg)

    opt_for_crawler=['language','output','silent']
    arguments_for_crawler = functools.reduce(
        lambda x, y: x + y, [f"{key}={value} " for key, value in arg.items() if key in opt_for_crawler], "")
    logging.info(f"Crawler starts with options: {arguments_for_crawler}")
    # call crawler with given parameters
    # command for running looks like: scrapy runspider spider.py -a [arg1=val1
    # arg2=val2 ...]

    # call(["scrapy", "runspider", os.path.join("crawler", "WikiSpider.py"),
    #      "-a", f'arg={arguments_for_crawler}'])

    # database_binding.DB_STRING.replace("localhost", arg["host"])

    multiprocess(count_workers=arg["concurrency"], args=arguments_for_crawler)
