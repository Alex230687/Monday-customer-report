"""Модуль содержит функции декораторы deco_page(), deco_tags()."""
from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def deco_page(page):
    """
    Параметризованный декоратор для проверки загруки страницы.

    Декоратор принимает url страницы
    Если во время загрузки возникает исключение - метод не выполняется
    """
    def decorator(method):
        def wrapper(self):
            try:
                self.driver.get(page)
            except (TimeoutException, InvalidArgumentException) as error:
                self.error(page, 'ОШИБКА ЗАГРУЗКИ СТРАНИЦЫ', error)
            else:
                method(self)
        return wrapper
    return decorator


def deco_tags(page, tags):
    """
    Параметризованный декоратор для проверки загруки страницы.

    Декоратор принимает url страницы и блок тегов DOM
    Если один из элементов не загружен за отведенное время генерируется исключение
    Аргумент page передаётся для занесения url в данные об исключении
    """
    def decorator(method):
        def wrapper(self):
            try:
                for name, tag in tags.items():
                    self.elements[name] = WebDriverWait(self.driver, 60).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, tag))
                    )
            except TimeoutException as error:
                self.error(page, 'ОШИБКА ЗАГРУЗКИ ТЕГОВ DOM', error)
            else:
                method(self)
        return wrapper
    return decorator
