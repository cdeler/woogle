import argparse
from subprocess import call


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run wiki-downloader&parser with given options.',
        epilog='File with spider MUST be in the same directory as this file. \
                The logic of processing arguments is inside called spider. \
                Arguments just define its behaviour depending on their values.')
    # define optional arguments
    parser.add_argument('-args', '--a', help='arguments to feed the crawler with', type=str, nargs='+')

    arg = parser.parse_args().a

    # call crawler with given parameters
    # command for running looks like: scrapy runspider spider.py -a [arguments]
    # that's why -a here(jnext line) is not the argument for this script - it goes with the spider
    if arg:
        call(["scrapy", "runspider", "WikiSpider.py", "-a", "arg={}".format(arg)])
    else:
        call(["scrapy", "runspider", "WikiSpider.py"])
