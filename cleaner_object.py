"""Модуль содрежит функцию cleaner."""
import os


def cleaner(path=None):
    """Функция получает директорию и удаляет из неё все файлы."""
    file_list = os.listdir(path)
    if file_list:
        for file in file_list:
            os.remove(os.path.join(path, file))
