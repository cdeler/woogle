import sys
sys.path.append(sys.path[0] + "/..")

import unittest
from src.PidFile import PidFile
from src.PidFile import CrawlerException
import os
from random import randint


class TestPidFile(unittest.TestCase):

    def test__file_not_exist__positive(self):
        name_file = f'test_pidfile_{randint(1,10000)}'

        with PidFile(path=os.path.curdir, name=name_file) as pidfile:
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
        name_file = f'test_pidfile_{randint(1,10000)}'
        # create file
        f = open(os.path.join(os.path.curdir, name_file), "x")
        f.close()

        with PidFile(path=os.path.curdir, name=name_file) as pidfile:
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
        name_file = f'test_pidfile_{randint(1,10000)}'

        # create file
        with open(os.path.join(os.path.curdir, name_file), "x"):
            with self.assertRaises(CrawlerException) as raised_exception:
                with PidFile(path=os.path.curdir, name=name_file):
                    pass
            self.assertEqual(raised_exception.exception.args, ())

        try:
            os.remove(os.path.join(os.path.curdir, name_file))
        except Exception:
            pass


if __name__ == '__main__':
    unittest.main()
