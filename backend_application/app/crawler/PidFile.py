
import os
import logging


class PidFile(object):
    """
    Contex manager for manage crawler launch
    """

    def __init__(self, path=os.path.curdir, name='pidfile'):
        self.path = path
        self.pidfile = None
        self.name = name

    def __enter__(self):
        try:
            self.pidfile = open(os.path.join(self.path, self.name), "x")
            self.pidfile.write('pid')
        except Exception:
            logging.debug('PidFile: pidfile exist')
            try:
                # если файл существует, проверяем свободен ли он
                os.remove(os.path.join(self.path, self.name))
            except Exception:
                logging.debug('PidFile: pidfile busy')
                raise CrawlerException()
            else:
                self.pidfile = open(os.path.join(self.path, self.name), "a")
                logging.debug('PidFile: pidfile open')
                return self.pidfile
        else:
            logging.debug('PidFile: pidfile open')
            return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
        except Exception:
            return
        else:
            logging.debug('PidFile: pidfile closed and removed')
            os.remove(os.path.join(self.path, self.name))


class CustomException(Exception):
    pass


class CrawlerException(CustomException):
    def __str__(self):
        return 'Crawler is already running. Wait for the crawler to complete and try again'
