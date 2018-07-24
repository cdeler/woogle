"""
pre-commit file for autoformiting python code by standart
arguments: --check {*} - do checking and autoformating python code. Default is DEFAULT_CHECKINF_FILE
           --exec  {*} - path of executer of checking file
"""
DEFAULT_CHECKINF_FILE = "autoformating_python_pep8.py"
import sys
import argparse
from os.path import abspath, dirname, join, basename
from subprocess import Popen, PIPE


def shell_command(command):
    """
    Execute shell comand
    :param command: command for executing
    :type command: list
    :return: code: int, report: stdout
    """
    # Execute subprocess
    proc = Popen(command, stdout=PIPE, stderr=PIPE)

    # Waiting for end
    proc.wait()

    # Function of for transform data
    # (convert to str, delete "\r\n")
    def transform(x): return ' '.join(x.decode('utf-8').split())

    # Reads and transforms flow stdout
    report = [transform(x) for x in proc.stdout]

    # Add flow stderr
    report.extend([transform(x) for x in proc.stderr])

    # Returns code subprocess and console output like like
    return proc.returncode, report


def head_revision():
    """
    Getting list of path's changing files
    :return: result code: int, targets: list of path files
    """

    # set code result
    result_code = 0
    # checking existence of git
    code, report = shell_command(
        ['git', '--version'])
    if code != 0:
        result_code = code
        print("Error: Git doesn't install ")

    # get list of files current commit
    code, report = shell_command(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'])
    if code != 0:
        result_code = code
        print("Error: can't get list of changed files")

    # filters file by "py"
    targets = filter(lambda x: x.split('.')[-1] == "py", report)

    # add absolute path to files
    targets = [join(dirname(abspath(x)), basename(x)) for x in targets]
    return result_code, targets


def formating_python_code(exec, name_comply_file, targets):
    """
    Formating target files by standart
    :param exec: path tu executer (python)
    :type exec: str
    :param name_comply_file: name of filef witch formating code
    :type name_comply_file: str
    :param targets: list of name of source files
    :param targets: list
    :return: result code - int
    """
    # execute file for autoformating
    code, report = shell_command(
        [exec, name_comply_file] + targets)

    for i in report:
        print(i)

    # git add change
    code, report = shell_command(
        ['git', 'add', '-u'])

    for i in report:
        print(i)

    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--check', nargs='*')
    parser.add_argument('-e', '--exec', default=sys.executable)
    params = vars(parser.parse_args(sys.argv[1:]))

    if params.get('check') is None:
        print("Don't create checking")

    if params.get('check') is not None and len(params.get('check')) == 0:
        params['check'] = [
            join(
                dirname(
                    abspath(__file__)),
                DEFAULT_CHECKINF_FILE)]

    # get changing python's file
    code, targets = head_revision()
    if code != 0:
        print("Error: can't get file")
        exit(1)
    if len(targets) != 0:
        # formating code
        code = formating_python_code(
            params.get('exec'),
            params.get('check')[0],
            targets)

        if code != 0:
            print("Error: can't autoformating")
            exit(1)

    print("File formated!")

    exit(0)
