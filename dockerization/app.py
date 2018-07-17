import argparse
from subprocess import call

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run wiki-downloader&parser with given options.',
        epilog='File with spider MUST be in the same directory as this file. \
                The logic of processing arguments is inside called spider. \
                Arguments just define its behaviour depending on their values.')
    # define optional arguments
    parser.add_argument('-a', '--args', help='arguments to feed the crawler with', type=str, nargs='+')

    arg = parser.parse_args().args
    print(arg)
    # call crawler with given parameters
    # command for running looks like: scrapy runspider spider.py -a [arguments]
    # that's why -a here(next line) is not the argument for this script - it goes with the spider
    call(["scrapy", "runspider", "WikiPage.py", "-a", "arg={}".format(arg)])
