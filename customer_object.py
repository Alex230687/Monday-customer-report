"""Модуль содержит классы BaseCustomer, Md, Mg, Ms, Bg."""
import time
from MD.settings import MD_SETTINGS
from MS.settings import MS_SETTINGS
from MG.settings import MG_SETTINGS
from BG.settings import BG_SETTINGS
from driver_object import Driver
from parser_object import ParserTypeOne, ParserTypeTwo
from file_object import File


class BaseCustomer:
    """
    Базовый класс. Определяет основную структуру производных классов.

    Атрибуты:
        SETTINGS - общий блок настроек по контрагента
    Методы:
        run_parser() - запуск программы выгрузки отчетных файлов
        get_data_from_file() - получение данных из выгруженных файлов
        run_program() - общий запуск выгруки и получения данных из файлов
    """
    SETTINGS = None

    def __init__(self, period, counter, period_id):
        """
        Конструктор принимает аргументы period, counterm period_id.

        :param period: период отчета
            DATE_START - datetime.date(year, month, day)
            DATE_END -  datetime.date(year, month, day)

        :param counter: глобальный счетчик itertools.count()
        :param period_id: номер текущего периода для SQL

        Атрибуты:
            driver - объект selenium.webdriver.Chrome()
            file - объект для работы с файлами отчетов
        """
        self.period = period
        self.counter = counter
        self.driver = Driver(settings=self.__class__.SETTINGS['DRIVER'])
        self.file = File(
            settings=self.__class__.SETTINGS['FILE'],
            period=self.period,
            counter=self.counter,
            period_id=period_id
        )

    def run_program(self):
        """Метод запускает выгрузки отчетов из ЛК и получает их данные."""
        self.run_parser()
        time.sleep(5)
        self.get_data_from_file()

    def run_parser(self):
        """Метод запускает программу выгрузки отчетов из ЛК."""
        parser = ParserTypeOne(
            settings=self.__class__.SETTINGS['PARSER'],
            driver_object=self.driver,
            period=self.period,
            counter=self.counter
        )
        parser.run_all()

    def get_data_from_file(self):
        """Метод получает данные из файлов."""
        self.file.run_file_program()


class Md(BaseCustomer):
    """
    Производный класс от BaseCustomer.

    Переопределён атрибут SETTINGS
    """
    SETTINGS = MD_SETTINGS


class Mg(BaseCustomer):
    """
    Производный класс от BaseCustomer.

    Переопределён атрибут SETTINGS
    """
    SETTINGS = MG_SETTINGS


class Ms(BaseCustomer):
    """
    Производный класс от BaseCustomer.

    Переопределён атрибут SETTINGS
    """
    SETTINGS = MS_SETTINGS


class Bg(BaseCustomer):
    """
    Производный класс от BaseCustomer.

    Переопределён атрибут SETTINGS
    Переопределён метод run_parser()
    """
    SETTINGS = BG_SETTINGS

    def run_parser(self):
        """
        Переопределён метод базового класса.

        Изменён тип используемого парсера на ParserTypeTwo
        """
        parser = ParserTypeTwo(
            settings=self.__class__.SETTINGS['PARSER'],
            driver_object=self.driver,
            period=self.period,
            counter=self.counter
        )
        parser.run_all()


CLASS_LIST = [Md, Mg, Ms, Bg,]
