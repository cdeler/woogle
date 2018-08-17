

import os
import logging
import sys


def PidFile(path=os.path.curdir, name='pidfile'):
    if sys.platform == 'linux':
        return PidFileLinux(path=path, name=name)
    elif sys.platform.find('win') != -1:
        return PidFileWin(path=path, name=name)
    else:
        raise OSError(
            f"Class PIdFile for this system ({sys.platform}) is not released")


class PidFileLinux(object):
    """
    Contex manager for manage crawler launch
    """

    def __init__(self, path=os.path.curdir, name='pidfile'):
        self.path = os.path.join(path, name)
        self.pidfile = None

    def __enter__(self):
        import fcntl
        logging.debug(f'PidFile:open pidfile: {self.path}')
        self.pidfile = open(self.path, "a+")
        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logging.debug(f'PidFile: pidfile busy: {self.path}')
            self.pidfile.close()
            raise CrawlerException()

        return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
            os.remove(self.path)
        except Exception:
            logging.debug('PidFile: unknow error in 31 line')
            return
        else:
            logging.debug('PidFile: pidfile closed and removed')


class PidFileWin(object):
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


if __name__ == "__main__":
    with PidFile():
        k = 0
        for i in range(10000):
            k += 1
            for j in range(5000):
                pass
    print('End')
