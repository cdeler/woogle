import argparse
import functools
from subprocess import call

MAX_COUNT_THREADS = 10
CHOICE_LANGUAGE = ['ru', 'en']
CHOICE_OUTPUT = ['stdout', 'db', 'directory']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run wiki-downloader&parser with given options.',
        epilog='File with spider MUST be in the same directory as this file. \
                The logic of processing arguments is inside called spider. \
                Arguments just define its behaviour depending on their values.')

    # define optional arguments
    parser.add_argument(
        '-n',
        '--num-threads',
        help='count threads (defalut: 1)',
        type=int,
        choices=range(
            1,
            MAX_COUNT_THREADS),
        default='1')
    parser.add_argument(
        '-l',
        '--language',
        help='wikipedia language (default: ru)',
        type=str,
        choices=CHOICE_LANGUAGE,
        default=CHOICE_LANGUAGE[0])
    parser.add_argument(
        '-o',
        '--output',
        help='output (default: stdout)',
        type=str,
        choices=CHOICE_OUTPUT,
        default=CHOICE_OUTPUT[0])
    arg_s = parser.add_argument(
        '-s',
        '--silent',
        help='turn on silent mode, use with output=stdout (default: False)',
        action='store_true')

    arg = vars(parser.parse_args())
    if arg['silent'] and arg['output'] != 'stdout':
        msg = "isn't used with argument -o|--output equal 'stdout'"
        raise argparse.ArgumentError(arg_s, msg)

    arguments_for_crawler = functools.reduce(
        lambda x, y: x + y, [f"{key}={value} " for key, value in arg.items()], "")
    print(arguments_for_crawler)
    # call crawler with given parameters
    # command for running looks like: scrapy runspider spider.py -a [arg1=val1
    # arg2=val2 ...]
    call(["scrapy", "runspider", "WikiSpider.py", "-a", arguments_for_crawler])
