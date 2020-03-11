"""Modul contains Sql class"""
from collections import namedtuple
import pyodbc


CheckTup = namedtuple('CheckTup', ['PERIOD_ID', 'DATE_START'])


class Sql:
    """
    Класс Sql. Обработка SQL запросов с БД MS SQL.

    create_connections() - создание подключения
    close_connections() - закрытие подключения
    existence_check() - проверка существования данных в БД
    insert_value() - загрука данных в БД
    """

    def __init__(self, settings):
        """
        Sql class constructor.

        settings - блок настроек SQL (настройки соединения, таблица данных)
        """
        self.settings = settings
        self.connection = None
        self.cursor = None
        self.check = CheckTup(0, 0)
        self.message = []

    def create_connection(self):
        """Метод создания текущего соединения."""
        self.connection = pyodbc.connect(**self.settings['SETTINGS'])
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """Метод закрытия текущего соединения."""
        self.cursor.close()
        self.connection.close()

    def existence_check(self, customer, register):
        """
        Метод для проверки существования данных в БД.

        Принимает имя контрагента и регистра в БД
        1. Получает максимальный номер периода и соответсвующую ему дату начала
        """
        self.check = CheckTup(0, 0)
        query = """
            SELECT A.НомерПериода, B.Дата_начало
            FROM {0} AS A
            INNER JOIN {0} AS B 
            ON A.НомерПериода = B.НомерПериода
            WHERE A.Партнер='{1}' AND A.Регистр='{2}' AND
            A.НомерПериода=(SELECT MAX(НомерПериода) FROM {0} WHERE Партнер='{1}' AND Регистр='{2}')
            GROUP BY A.НомерПериода, B.Дата_начало
        """.format(self.settings['TABLE'], customer, register)
        if self.connection and self.cursor:
            try:
                self.cursor.execute(query)
            except pyodbc.Error as err:
                msg = "Ошибка проверки наличия данных в БД ({0}, {1}, err_text='{2}')".format(
                    customer, register, err
                )
                self.message.append(msg)
            else:
                self.check = CheckTup(*self.cursor.fetchall()[0])

    def insert_values(self, data_list):
        """Запись данных в БД."""
        query = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % self.settings['TABLE']
        try:
            self.cursor.executemany(query, data_list)
        except pyodbc.Error as err:
            msg = "Ошибка загрузки данных в БД (запрос='{0}', err_text='{1}')".format(query, err)
            self.message.append(msg)
        else:
            self.connection.commit()
