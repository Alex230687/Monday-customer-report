"""Модуль содержит класс Customer."""
import time
from driver_object import Driver
from parser_object import parser_types
from file_object import File


class Customer:
    """Класс Customer."""

    def __init__(self, settings, period, period_id):
        """
        Конструктор класса Customer

        settings - принимает общий блок настроек контрагента
        period - dict() объектов datetime.date(year, month, day)
        period_id - int() значения для записи в поле НомерПериода

        parser_cls - dict() классов прасера
        driver - объект вебдрайвера
        file - объект класса File
        message - блок сообщений программы
        """
        self.settings = settings
        self.period = period
        self.parser_cls = parser_types[str(self.settings['PARSER']['TYPE'])]
        self.driver = Driver(settings=self.settings['DRIVER'])
        self.file = File(settings=self.settings['FILE'], period=self.period, period_id=period_id)
        self.message = []

    def run_program(self, register):
        """Метода запускает основной блок программы."""
        self.run_parser(register)
        time.sleep(5)
        self.get_data_from_file()
        self.message += self.file.message

    def run_parser(self, register):
        """
        Метод запуска парсера.

        Принимает строковое представление регистра БД ('ALL', 'SALES', 'RESTS')
        1. Создание объекта парсера
        2. Запуск блока парсера по преданному регистру
        """
        parser = self.parser_cls(settings=self.settings['PARSER'], driver_object=self.driver,
                             period=self.period,)
        if register == 'ALL':
            parser.run_all()
        elif register == 'SALES':
            parser.run_sales()
        elif register == 'RESTS':
            parser.run_rests()
        self.message += parser.message

    def get_data_from_file(self):
        """Метод получает данные из файлов."""
        self.file.run_file_program()
