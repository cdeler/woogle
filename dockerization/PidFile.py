
import os


class PidFile(object):

    def __init__(self, path=os.path.curdir):
        self.path = path
        self.pidfile = None
        self.name = 'pidfile'

    def __enter__(self):
        try:
            # если файла не сущестует то открываем его
            self.pidfile = open(os.path.join(self.path, self.name), "x")
            self.pidfile.write('pid')
        except Exception:
            #print('Файл существует')
            try:
                # если файл существует, проверяем свободен ли он
                os.remove(os.path.join(self.path, self.name))
            except Exception:
                #print('Файл занят')
                raise PermissionError(
                    'Crawler is already running. Wait for the crawler to complete and try again.')
            else:
                self.pidfile = open(os.path.join(self.path, self.name), "a")
                #print('Файл открыт')
                return self.pidfile
        else:
            #print('Файл создан')
            return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
        except Exception as e:
            return
        else:
            #print('Файл закрыт и удален')
            os.remove(os.path.join(self.path, self.name))
