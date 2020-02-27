"""Модуль содержит класс File."""
import os
from bs4 import BeautifulSoup


class File:
    """
    Класс File.

    Атрибуты:
        ERROR - словарь для сбора данных о перехваченных исключениях

    Методы:
        error() -
    """
    ERROR = dict()

    def __init__(self, settings, period, counter, period_id):
        """
        Конструктор принимает аргументы settings, period, counter, period_id.

        :param settings: блок основных настроек
            SQL_NAME - наименование для записи в БД
            BASE_DIR - директория расположения файлов
            ENCODING - кодировка файла
            FILE_PATTERN - подстрока поиска файла
                SALES_PATTERN - подстрока файла отчета продаж
                RESTS_PATTERN - подстрока файла отчета остатков
            SALES_CYCLE - namedtuple() см. parse_cycle
            RESTS_CYCLE - namedtyple() см. parse_cycle
        :param period: - период отчета
            DATE_START - datetime.date(year, month, day)
            DATE_END - datetime.date(year, month, day)
        :param counter: - глобальный счетчик itertools.count()
        :param period_id: - номер текущего периода для БД
        """
        self.settings = settings
        self.period = period
        self.counter = counter
        self.period_id = period_id
        self.sales_list = None
        self.rests_list = None

    def error(self, directory, error_text):
        """Метод добавляет в атрибут класса данные об исключении."""
        self.__class__.ERROR[str(next(self.counter))] = {
            'ERROR TYPE': 'Ошибка чтения файла',
            'ERROR DIR': directory,
            'ERROR TEXT': error_text,
        }

    def run_file_program(self):
        """
        Метод поиска файлов и получения данных.

        1. Определение директории расположения файлов контрагента
        2. Получение списка имён файлов в директории
        3. Определение типа отчета и пусти к файлу
        4. Запуск метода get_data_from_file

        Присвоение атрибутам экземпляра sales_list, rests_list новых значений
        """
        base_dir = self.settings['BASE_DIR']
        file_list = os.listdir(base_dir)
        if file_list:
            for file in file_list:
                if self.settings['FILE_PATTERN']['SALES_PATTERN'] in file:
                    sales_file_path = os.path.join(base_dir, file)
                    self.sales_list = self.get_data_from_file(
                        file_path=sales_file_path,
                        cycle=self.settings['SALES_CYCLE'],
                        register='SALES'
                    )
                elif self.settings['FILE_PATTERN']['RESTS_PATTERN'] in file:
                    rests_file_path = os.path.join(base_dir, file)
                    self.rests_list = self.get_data_from_file(
                        file_path=rests_file_path,
                        cycle=self.settings['RESTS_CYCLE'],
                        register='RESTS'
                    )
                else:
                    self.error(file, 'Файл отсутствует в текущей директории')
        else:
            self.error(base_dir, 'Директория пуста')

    def get_data_from_file(self, file_path, cycle, register):
        """
        Метод получает данные из файла отчета.

        Метод принимает аргументы:
            file_path - путь к файлу отчета
            cycle - namedtuple() с ключевыми позициями, см. parse_cycle()
            registr - строка со значением поля регистра, см. parse_cycle()

        1. Открытие файла через менеджер контекста
        2. Передача данных файла в объект BeautifulSoup()
        3. Выборка данных по тегу ячейки <td>
        4. Зпуск метода parse_cycle()

        Возвращает список кортежей data_list или None если список пуст
        """
        data_list = None
        with open(file_path, mode='r', encoding=self.settings['ENCODING']) as file:
            soup = BeautifulSoup(file.read(), 'lxml')
            soup_rows = soup.findAll('td')
            data_list = self.parse_cycle(soup_rows, cycle, register)
        if not data_list:
            return None
        return data_list

    def parse_cycle(self, soup_rows, cycle, register):
        """
        Метод запускает обход xml таблицы и записывает данные в список.

        Метод принимает аргументы:
            soup_rows - выборка объекта BeautifulSoup()
            cycle - namedtuple(START, STOP, STEP, ISBN, QUANTITY, QUANTITY_ADD)
                START - начало диапазона
                STOP - корректировка окончания диапазона
                STEP - шаг
                ISBN - оффсет позиции артикула
                QUANTITY - оффсет позиции количества
                QUANTITY_ADD - оффсет доп.колонки количества (не у всех)
            register - значение поля регистра str() 'SALES' / 'RESTS'

        1. Обьявление переменной data_list
        2. Конвертация объектов datetime в формат YYYY-MM-DD
        3. Цикл обхода строк xml таблицы и запись данных

        Возвращает список кортежей data_list или None если список пуст
        """
        data_list = []
        date_start = self.period['DATE_START'].isoformat()
        date_end = self.period['DATE_END'].isoformat()
        for row in range(cycle.START, len(soup_rows)-cycle.STOP, cycle.STEP):
            isbn = soup_rows[row+cycle.ISBN].get_text()
            quantity = int(soup_rows[row+cycle.QUANTITY].get_text())
            if hasattr(cycle, 'QUANTITY_ADD') and cycle.QUANTITY_ADD:
                quantity += int(soup_rows[row+cycle.QUANTITY_ADD].get_text())
            data_list.append(
                (
                    self.settings['SQL_NAME'],  # SQL field: Партнер
                    isbn,                       # SQL field: ISBN
                    quantity,                   # SQL field: Количество
                    register,                   # SQL field: Регистр
                    date_start,                 # SQL field: Дата_начало
                    date_end,                   # SQL filed: Дата_конец
                    self.period_id              # SQL field: НомерПериода
                )
            )
        if not data_list:
            return None
        return data_list
