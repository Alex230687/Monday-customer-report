"""Module contains File class"""
import os
from bs4 import BeautifulSoup


class File:
    """
    Класс File для обработки xml файлов.

    run_file_program() - основной метод запускающий поиск файлов и сбор данных
    """

    def __init__(self, settings, period, period_id):
        """
        Конструктор класса File.

        settings - блок настроек ['FILE']
        period - dict() объектов datetime.date(year, month, day)
        period_id - int() значения для записи в поле НомерПериода

        sales_list - данные отчета продаж
        rests_list - данные отчета остатков
        message - блок сообщений программы
        """
        self.settings = settings
        self.period = period
        self.period_id = period_id
        self.sales_list = None
        self.rests_list = None
        self.message = []

    def run_file_program(self):
        """
        Основной метод для поиска файлов и получения данных.

        1. Определение директории и списка файлов этой директроии
        2. Обход списка файлов и получение данных, формирование программных сообщений
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
                    if not self.sales_list:
                        msg = "Файл продаж не найден или пуст ({0}, {1})".format(
                            self.settings['SQL_NAME'], sales_file_path
                        )
                        self.message.append(msg)
                elif self.settings['FILE_PATTERN']['RESTS_PATTERN'] in file:
                    rests_file_path = os.path.join(base_dir, file)
                    self.rests_list = self.get_data_from_file(
                        file_path=rests_file_path,
                        cycle=self.settings['RESTS_CYCLE'],
                        register='RESTS'
                    )
                else:
                    msg = "Файл не найден по подстроке '{0}' и '{1}' ({1}, {2})".format(
                        self.settings['FILE_PATTERN']['SALES_PATTERN'],
                        self.settings['FILE_PATTERN']['RESTS_PATTERN'], self.settings['SQL_NAME'],
                        base_dir)
                    self.message.append(msg)
            if not self.sales_list:
                msg = "Файл продаж не найден или пуст ({0})".format(self.settings['SQL_NAME'])
                self.message.append(msg)
            if not self.rests_list:
                msg = "Файл остатков не найден или пуст ({0})".format(self.settings['SQL_NAME'])
                self.message.append(msg)
        else:
            msg = "Файлы отсутствуют ({0}, {1})".format(self.settings['SQL_NAME'], base_dir)
            self.message.append(msg)

    def get_data_from_file(self, file_path, cycle, register):
        """
        Метод для получения данных из файла.

        1. Открытие файла и создание объекта BeautifulSoup
        2. Запуск цикла обработки таблицы xml
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
        Метод для обхода xml таблицы и получения данных.

        Принимает объект выборки BeautifulSoup, цикл обработки и регистр отчета
        1. Получение строкового представления периода
        2. Построчный обход xml и формирование блоков строк для записи в БД
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
                    self.period_id[register]    # SQL field: НомерПериода
                )
            )
        if not data_list:
            return None
        return data_list
