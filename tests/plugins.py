from pathlib import Path

SKIP_DIRS = {Path('tests/factories'), }
SKIP_FILENAMES = {'fixtures.py', 'plugins.py', }


def inside_skip_dirs(path):
    return any(
        path.is_relative_to(_p) for _p in SKIP_DIRS
    )


def pytest_sessionstart(session):
    """
    Проверяем, чтобы все тестовые файлы начинались test_.
    Иначе они игноряться при нахождении тестов.
    """
    all_files = Path('tests').rglob('*.py')
    for file in all_files:
        if not inside_skip_dirs(file) and file.name not in SKIP_FILENAMES:
            if not file.match('test_*.py'):
                raise AssertionError(
                    f'File {file} name should starts with "test_" !!!',
                )
