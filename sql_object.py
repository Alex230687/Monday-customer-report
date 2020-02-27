"""Модуль содержит классс Sql"""
import pyodbc


class Sql:
    """
    Класс Sql.

    АРИБУТЫ:
        ERROR - словарь для сбора данных о перехваченных исключениях

    МЕТОДЫ:
        error() - обработка ошибок
        create_connection() - создание соединения
        close_connection() - закрытие соединения
        get_period_id() - получение номера периода
        insert_values() - загрузка данных в SQL
    """
    ERROR = dict()

    def __init__(self, settings, counter):
        """
        Конструктор принимает аргументы settings, period, counter, period_id.

        :param settings: блок основных настроек MS SQL
            SETTINGS - настройки подключения
                DRIVER, SERVER, DATABASE, UID, PWD
            TABLE - таблица БД для загруки отчетов

        :param counter: - глобальный счетчик itertools.count()
        """
        self.settings = settings
        self.counter = counter
        self.connection = None
        self.cursor = None
        self.period_id = None

    def error(self, error_query, error_type, error_text, error_data=None):
        """Метод добавляет в атрибут класса данные об исключении."""
        self.__class__.ERROR[str(next(self.counter))] = {
            'ERROR_QUERY': error_query,
            'ERROR_TYPE': error_type,
            'ERROR_TEXT': error_text,
            'ERROR_DATA': error_data
        }

    def create_connection(self):
        """Метод создает объект подключения и курсора."""
        self.connection = pyodbc.connect(**self.settings['SETTINGS'])
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """Метод закрывает текущее соединение."""
        self.cursor.close()
        self.connection.close()

    def get_period_id(self):
        """Метод получает максимальный период из БД и добавляет к нему 1."""
        if self.connection and self.cursor:
            query = "SELECT MAX(НомерПериода) as mpid FROM %s" % self.settings['TABLE']
            try:
                self.cursor.execute(query)
            except pyodbc.Error as error:
                self.error(query, 'ОШИБКА ПОЛУЧЕНИЯ НОМЕРА ПЕРИОДА', error)
            else:
                sql_id = self.cursor.fetchone().mpid
                if sql_id is None:
                    self.period_id = 1
                else:
                    self.period_id = int(sql_id) + 1

    def insert_values(self, data_list):
        """Метод получет список данных и добваляет его в таблицу БД."""
        query = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % self.settings['TABLE']
        try:
            self.cursor.executemany(query, data_list)
        except pyodbc.Error as error:
            self.error(query, 'ОШИБКА ЗАПИСИ В БД', error)
        else:
            self.connection.commit()
