"""Модуль содержит функции декораторы deco_page(), deco_tags()."""
from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def deco_page(page):
    """Параметризованный декоратор для проверки загруки страницы."""
    def decorator(method):
        def wrapper(self):
            try:
                self.driver.get(page)
            except (TimeoutException, InvalidArgumentException) as error:
                customer = self.settings['PASRER']['CUSTOMER']
                msg = "Страница {0} не загружена ({1})".format(page, customer)
                self.message.append(msg)
            else:
                method(self)
        return wrapper
    return decorator


def deco_tags(tags):
    """Параметризованный декоратор для проверки загруки ключевых элементов DOM."""
    def decorator(method):
        def wrapper(self):
            try:
                for name, tag in tags.items():
                    self.elements[name] = WebDriverWait(self.driver, 60).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, tag))
                    )
            except TimeoutException as error:
                customer = self.settings['PARSER']['CUSTOMER']
                page = self.driver.current_url
                msg = "Ключевые теги страницы {0} не загружены ({1})".format(page, customer)
                self.message.append(msg)
            else:
                method(self)
        return wrapper
    return decorator
