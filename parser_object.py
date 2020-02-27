"""Модуль содержит классы BaseParser, ParserTypeOne, ParserTypeTwo"""
from copy import copy
from selenium.webdriver.common.action_chains import ActionChains
from decorator import deco_page, deco_tags


class BaseParser:
    """
    Родительский класс BaseParser.

    Атрибуты:
        ERROR - словарь данных об ошибках

    Методы:
        error(error_page, error_type, error_text) - данные об исключении
        auth() - авторизация на сайте
        sales() - загрузка отчета продаж
        rests() - загрузка
        run_all() - запуск авторизации, загрузка продаж и остатков
        run_sales() - запуск авторизации, загрузка продаж
    """
    ERROR = dict()

    def __init__(self, settings, driver_object, period, counter):
        """
        Конструктор класса BaseParser. Принимает блок настроек, период и счетчик.

        :param settings: - блок основных настроек парсера <class dict>
            CUSTOMER - наименование контрагента
            UD - данные авторизации
                LOGIN - логин
                PWD - пароль
            PAGE - ключевые страницы
                AUTH_PAGE - страница авторизации
                SALES_PAGE - страница продаж
                RESTS_PAGE - страница остатков
            AUTH - теги авторизации
            SALES - теги отчета продаж
            RESTS - теги отчета остатков

        :param driver_object: - блок настроек вебдрайвера
            PATH - путь к файлу драйвера chromedriver.exe
            SPEED - определение pageLoadStrategy
            DOWNLOAD - директория загруки файлов

        :param period: - период отчета
            DATE_START - datetime.date(year, month, day)
            DATE_END - datetime.date(year, month, day)

        :param counter: - глобальный счетчит itertools.count()

        Атрибуты:
            elements() - словарь определённых и загруженных элементов DOM
        """
        self.settings = settings
        self.driver = driver_object()
        self.period = period
        self.counter = counter
        self.elements = dict()

    def error(self, error_page, error_type, error_text):
        """Метод записывает инфорацию об исключении в атрибут класса ERROR."""
        self.__class__.ERROR[str(next(self.counter))] = {
            'CUSTOMER': self.settings['CUSTOMER'],
            'ERROR_PAGE': error_page,
            'ERROR_TYPE': error_type,
            'ERROR_TEXT': error_text,
        }

    def run_all(self):
        """Метод запускает полный цикл автризации и загрузки отчетов."""
        self.auth()(self)
        self.sales()(self)
        self.rests()(self)
        self.driver.quit()

    def run_sales(self):
        """Метод запускает цикл авторизции и выгрузки отчета продаж."""
        self.auth()(self)
        self.sales()(self)
        self.driver.quit()

    def run_rests(self):
        """Метод запускает цикл авторизции и выгрузки отчета остатков."""
        self.auth()(self)
        self.sales()(self)
        self.driver.quit()

    def auth(self):
        """Метод выполняет авторизцаию в личном кабинете."""
        loaded_page = self.settings['PAGE']['AUTH_PAGE']
        loaded_tags = self.settings['AUTH']
        login = self.settings['UD']['LOGIN']
        password = self.settings['UD']['PWD']

        @deco_page(loaded_page)
        @deco_tags(loaded_page, loaded_tags)
        def auth_chain(self):
            """Метод запускает цепочку событий авторизации."""
            actions = ActionChains(self.driver)
            actions.pause(5)
            actions.send_keys_to_element(self.elements['LOGIN_TAG'], login)
            actions.send_keys_to_element(self.elements['PWD_TAG'], password)
            actions.pause(5)
            actions.click(self.elements['AUTH_BTN_TAG'])
            actions.pause(5)
            actions.perform()

        return auth_chain

    def sales(self):
        """Метод выполняет выгрузку файла продаж."""
        loaded_page = self.settings['PAGE']['SALES_PAGE'](**self.period)
        loaded_tags = self.settings['SALES']

        @deco_page(loaded_page)
        @deco_tags(loaded_page, loaded_tags)
        def sales_chain(self):
            """Метод запускает цепочку событий выгрузки отчета продаж."""
            actions = ActionChains(self.driver)
            actions.pause(5)
            actions.click(self.elements['SALES_BTN'])
            actions.pause(5)
            actions.perform()

        return sales_chain

    def rests(self):
        """Метод выполняет выгрузку файла остатков."""
        loaded_page = self.settings['PAGE']['RESTS_PAGE']
        loaded_tags = self.settings['RESTS']

        @deco_page(loaded_page)
        @deco_tags(loaded_page, loaded_tags)
        def rests_chain(self):
            """Метод запускает цепочку событий выгрузки отчета остатков."""
            actions = ActionChains(self.driver)
            actions.pause(5)
            actions.click(self.elements['RESTS_BTN'])
            actions.pause(5)
            actions.perform()

        return rests_chain


class ParserTypeOne(BaseParser):
    """Производный класс для определения типа парсера №1."""
    pass


class ParserTypeTwo(BaseParser):
    """
    Производный класс для определения типа парсера N2.

    Настройки парсера определённые конструктором базового класса
    дополняются вспомогательными элементами:
    SUB_TAGS - дополнительные элементы DOM для формирования отчета
    EXCEL_BTN - дполнительные элементы DOM для выгрузки файла
    """
    def sales(self):
        """Переопредел метод родительского класса."""
        loaded_page = self.settings['PAGE']['SALES_PAGE']
        loaded_tags = copy(self.settings['SALES'])
        loaded_tags.update(self.settings['SUB_TAGS'])
        excel_tag = self.settings['EXCEL_BTN']
        date_start = self.period['DATE_START']
        date_end = self.period['DATE_END']

        @deco_page(loaded_page)
        @deco_tags(loaded_page, loaded_tags)
        def sales_chain(self):
            """Метод запускает цепочку событий запроса страницы отчета продаж."""
            for key in ('START_DD', 'START_MM', 'START_YYYY', 'END_DD', 'END_MM', 'END_YYYY'):
                self.elements[key].clear()
            actions = ActionChains(self.driver)
            actions.pause(5)
            actions.send_keys_to_element(self.elements['START_DD'], date_start.day)
            actions.send_keys_to_element(self.elements['START_MM'], date_start.month)
            actions.send_keys_to_element(self.elements['START_YYYY'], date_start.year)
            actions.send_keys_to_element(self.elements['END_DD'], date_end.day)
            actions.send_keys_to_element(self.elements['END_MM'], date_end.month)
            actions.send_keys_to_element(self.elements['END_YYYY'], date_end.year)
            actions.click(self.elements['CHECK'])
            actions.pause(5)
            actions.click(self.elements['REPORT_BTN'])
            actions.pause(5)
            actions.perform()

            @deco_tags(loaded_page, excel_tag)
            def sub_sales_chain(self):
                """Метод запускает цепочку событий выгрузки отчета продаж."""
                sub_actions = ActionChains(self.driver)
                sub_actions.pause(5)
                sub_actions.click(self.elements['FILE_LOAD_BNT'])
                sub_actions.pause(10)
                sub_actions.perform()

            sub_sales_chain(self)

        return sales_chain

    def rests(self):
        """Переопредел метод родительского класса."""
        loaded_page = self.settings['PAGE']['RESTS_PAGE']
        loaded_tags = copy(self.settings['RESTS'])
        loaded_tags.update(self.settings['SUB_TAGS'])
        excel_tag = self.settings['EXCEL_BTN']

        @deco_page(loaded_page)
        @deco_tags(loaded_page, loaded_tags)
        def rests_chain(self):
            """Метод запускает цепочку событий запроса страницы отчета остатков."""
            actions = ActionChains(self.driver)
            actions.pause(5)
            actions.click(self.elements['CHECK'])
            actions.pause(5)
            actions.click(self.elements['REPORT_BTN'])
            actions.pause(5)
            actions.perform()

            @deco_tags(loaded_page, excel_tag)
            def sub_rests_chain(self):
                """Метод запускает цепочку событий выгрузки отчета остатков."""
                sub_actions = ActionChains(self.driver)
                sub_actions.pause(5)
                sub_actions.click(self.elements['FILE_LOAD_BNT'])
                sub_actions.pause(10)
                sub_actions.perform()

            sub_rests_chain(self)

        return rests_chain
