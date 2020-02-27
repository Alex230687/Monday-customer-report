"""Модуль содержит класс Driver."""
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as DC


class Driver:
    """Класс Driver."""

    def __init__(self, settings):
        """
        Конуструктор принимает блок настроек settings.

        :param settings: словарь с базовыми настройками драйвера
            PATH - пусть к файлу драйвера chromedriver.exe
            SPEED - параметр для pageLoadStrategy
            DOWNLOAD - директория сохранения файлов

        Атрибуты:
            settings - блок настроек
            driver_options - настройки драйвера
            driver_capabilites - доп.возможности драйвера
        """
        self.settings = settings
        self.driver_options = ChromeOptions()
        self.driver_capabilities = DC().CHROME

    def set_options(self):
        """Метод устанавливает основные настройки драйвера."""
        # self.driver_options.add_argument('--headless')
        self.driver_options.add_experimental_option(
            'prefs', {'download.default_directory': self.settings['DOWNLOAD']}
        )

    def set_capabilities(self):
        """Метод устанавливает дополнительные возможности драйвера."""
        if self.settings['SPEED'] == 'fast':
            self.driver_capabilities['pageLoadStrategy'] = 'none'

    def __call__(self):
        """Возвращает объект selenium.webdriver."""
        self.set_options()
        self.set_capabilities()
        driver = webdriver.Chrome(
            executable_path=self.settings['PATH'],
            chrome_options=self.driver_options,
            desired_capabilities=self.driver_capabilities
        )
        return driver
