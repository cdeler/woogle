import sys
sys.path.append(sys.path[0] + "/..")

import unittest
from src.PidFile import PidFileWin
from src.PidFile import PidFileLinux
from src.PidFile import CrawlerException
import os
from random import randint


class TestPidFileWin(unittest.TestCase):

    def test__file_not_exist__positive(self):
        if sys.platform.find('win') != -1:
            name_file = f'test_pidfile_{randint(1,10000)}'

            with PidFileWin(path=os.path.curdir, name=name_file) as pidfile:
                # check_pidfile
                self.assertIsNotNone(pidfile)

                # check exist
                self.assertTrue(
                    os.path.exists(
                        os.path.join(
                            os.path.curdir,
                            name_file)))
                # check busy
                with self.assertRaises(PermissionError) as raised_exception:
                    os.remove(os.path.join(os.path.curdir, name_file))
                self.assertEqual(raised_exception.exception.args[0], 13)

            # check remove
            self.assertFalse(
                os.path.exists(
                    os.path.join(
                        os.path.curdir,
                        name_file)))

            try:
                os.remove(os.path.join(os.path.curdir, name_file))
            except Exception:
                pass

    def test__file_exist_and_not_busy__positive(self):
        if sys.platform.find('win') != -1:
            name_file = f'test_pidfile_{randint(1,10000)}'
            # create file
            f = open(os.path.join(os.path.curdir, name_file), "x")
            f.close()

            with PidFileWin(path=os.path.curdir, name=name_file) as pidfile:
                # check_pidfile
                self.assertIsNotNone(pidfile)

                # check exist
                self.assertTrue(
                    os.path.exists(
                        os.path.join(
                            os.path.curdir,
                            name_file)))
                # check busy
                with self.assertRaises(PermissionError) as raised_exception:
                    os.remove(os.path.join(os.path.curdir, name_file))
                self.assertEqual(raised_exception.exception.args[0], 13)

            # check remove
            self.assertFalse(
                os.path.exists(
                    os.path.join(
                        os.path.curdir,
                        name_file)))

            try:
                os.remove(os.path.join(os.path.curdir, name_file))
            except Exception:
                pass

    def test__file_exist_and_busy__nonpositive(self):
        if sys.platform.find('win') != -1:
            name_file = f'test_pidfile_{randint(1,10000)}'

            # create file
            with open(os.path.join(os.path.curdir, name_file), "x"):
                with self.assertRaises(CrawlerException) as raised_exception:
                    with PidFileWin(path=os.path.curdir, name=name_file):
                        pass
                self.assertEqual(raised_exception.exception.args, ())

            try:
                os.remove(os.path.join(os.path.curdir, name_file))
            except Exception:
                pass


class TestPidFileLinux(unittest.TestCase):

    def test__positive(self):
        import fcntl

        name_file = f'test_pidfile_{randint(1,10000)}'

        with PidFileLinux(path=os.path.curdir, name=name_file) as pidfile:
            # check_pidfile
            self.assertIsNotNone(pidfile)

            # check exist
            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        os.path.curdir,
                        name_file)))
            # check busy
            test_open = open(os.path.join(
                os.path.curdir,
                name_file), "a+")
            with self.assertRaises(IOError) as raised_exception:
                fcntl.flock(test_open.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(raised_exception.exception.args[0], 11)

        # check remove
        self.assertFalse(
            os.path.exists(
                os.path.join(
                    os.path.curdir,
                    name_file)))

        try:
            os.remove(os.path.join(os.path.curdir, name_file))
        except Exception:
            pass

    def test__file_exist_and_busy__nonpositive(self):
        import fcntl

        name_file = f'test_pidfile_{randint(1,10000)}'

        # create file
        with PidFileLinux(path=os.path.curdir, name=name_file):
            with self.assertRaises(CrawlerException) as raised_exception:
                with PidFileLinux(path=os.path.curdir, name=name_file):
                    pass
            self.assertEqual(raised_exception.exception.args, ())

        try:
            os.remove(os.path.join(os.path.curdir, name_file))
        except Exception:
            pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    if sys.platform == 'linux':
        suite.addTests(
            unittest.TestLoader().loadTestsFromTestCase(TestPidFileLinux))
    elif sys.platform.find('win') != -1:
        suite.addTests(
            unittest.TestLoader().loadTestsFromTestCase(TestPidFileWin))
    else:
        raise OSError(
            f"Class PIdFile for this system ({sys.platform}) is not released")
    runner = unittest.TextTestRunner()
    runner.run(suite)
