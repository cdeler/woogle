import sys
import argparse
from os.path import abspath, dirname, join, basename
from subprocess import Popen, PIPE

def shell_command(command):
    # Запускаем подпроцесс
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    # Ожидаем его завершения
    proc.wait()
    # Функция для преобразования данных
    #    (конвертируем в строку, удаляем "\r\n")
    transform = lambda x: ' '.join(x.decode('utf-8').split())
    # Считываем (и преобразуем) поток stdout
    report = [transform(x) for x in proc.stdout]
    # Добавляем поток stderr
    report.extend([transform(x) for x in proc.stderr])

    # Возвращаем код завершения подпроцесса и консольный вывод в виде списка
    return proc.returncode, report


def head_revision():
    # Устанавливаем глобальный код результата
    result_code = 0
    # проверяем существует ли гит
    code, report = shell_command(
        ['git', '--version'])
    if code != 0:
        result_code = code
        print("Error: Git doesn't install ")

    # Получаем список файлов текущего commit'а
    code, report = shell_command(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'])
    if code != 0:
        result_code = code
        print("Error: can't get list of changed files")

    # Фильтруем файлы по расширению "py"
    targets = filter(lambda x: x.split('.')[-1] == "py", report)
    # Добавляем каждому файлу путь (текущий каталог проекта)
    targets = [join(dirname(abspath(x)), basename(x)) for x in targets]
    return result_code, targets

def formating_python_code(exec,name_comply_file, targets):
    code,report=shell_command(
        [exec,name_comply_file]+ targets)
        
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
        params['check'] = [join(dirname(abspath(__file__)), 'autoformating_python_pep8.py')]

    code, targets = head_revision()
    if code != 0:
        print("Error: can't get file")
        exit(1)


    code = formating_python_code(params.get('exec'),params.get('check'),targets)
    if code != 0:
        print("Error: can't autoformating")
        exit(1)

    print("File formated!")
    exit(0)
