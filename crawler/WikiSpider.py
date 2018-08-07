import scrapy
import WikiResponseProcessor

def arg_str2dict(arg):
    """
    Converting argument from "arg1=va1 arg2=val2 ..." to dict {arg1:va1, arg2:val2, ...}
    :param args: str
    :return: dict
    """
    try:
        arg_dict = {i.split('=')[0]: i.split('=')[1] for i in arg.split()}
    except Exception as e:
        raise TypeError(
            "Invalid format argument:\n f{arg} \n Correct format: 'arg1=va1 arg2=val2 ...' ") from e

    if 'silent' in arg_dict:
        if arg_dict['silent'] == "False":
            arg_dict['silent'] = False
        elif arg_dict['silent'] == "True":
            arg_dict['silent'] = True
        else:
            raise ValueError(
                f"Invalid mode silent - {arg_dict['silent']}. Correct value of argument 'silent' - True, False ")

    return arg_dict

def arg_str2dict(arg):
    """
    Converting argument from "arg1=va1 arg2=val2 ..." to dict {arg1:va1, arg2:val2, ...}
    :param args: str
    :return: dict
    """
    try:
        arg_dict = {i.split('=')[0]: i.split('=')[1] for i in arg.split()}
    except Exception as e:
        raise TypeError(
            "Invalid format argument:\n f{arg} \n Correct format: 'arg1=va1 arg2=val2 ...' ") from e

    if 'silent' in arg_dict:
        if arg_dict['silent'] == "False":
            arg_dict['silent'] = False
        elif arg_dict['silent'] == "True":
            arg_dict['silent'] = True
        else:
            raise ValueError(
                f"Invalid mode silent - {arg_dict['silent']}. Correct value of argument 'silent' - True, False ")

    return arg_dict


class WikiSpider(scrapy.Spider):
    name = 'WikiSpider'

    start_urls = [
        'https://ru.wikipedia.org/w/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%81%D0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
    ]
    allowed_domains = ['ru.wikipedia.org', ]

    def __init__(self, arg=None):
        """
        Getting next arguments in format: arg1=va1 arg2=val2 ...":
            num_threads: count threads
            language: wikipedia language (ru, en)
            output: output (stdout, db, directory)
            silent: flag, turn on silent mode, use with output=stdout
        :param arg: agrument for crawler
        :type arg: str
        """
        super(WikiSpider, self).__init__()
        if arg is not None:
            self.args = arg_str2dict(arg)
        else:
            self.args = arg

    def parse(self, response):
        """ Method that parses page of wiki articles' list
        :param response:
        :return:
        """
        yield from self.parse_wiki_pages(response)

        next_page = response.xpath(
            '//a[contains(text(), "Следующая страница")]/@href').extract_first()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_wiki_pages(self, response):
        """ Method that calls parsing processor for wiki articles
        :param response:
        :return:
        """

        self.processor = WikiResponseProcessor.WikiResponseProcessor.getWikiResponseProcessor(
            self.args)

        # if output=stdout
        if self.args is not None and 'output' in self.args and 'silent' in self.args:
            self.processor.process(response, silent=self.args['silent'])
        else:
            self.processor.process(response)

        pages = response.xpath(
            '//ul[@class="mw-allpages-chunk"]//a/@href').extract()
        for page in pages:
            if page is not None:
yield response.follow(page, callback=self.parse_wiki_pages)
