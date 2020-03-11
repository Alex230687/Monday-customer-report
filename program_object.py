"""Модуль содержит класс Program."""
import datetime
from customer_object import Customer
from cleaner_object import cleaner
from sql_object import Sql


class Program:
    """Класс основной программы."""

    def __init__(self, period, sql_settings, customer_settings):
        """Конструктор класса Program."""
        self.period = period
        self.sql_object = Sql(sql_settings)
        self.settings_list = customer_settings
        self.period_id = {'SALES': None, 'RESTS': None}
        self.message = []

    def register_status_check(self, customer, sql_register):
        """Метод проверяет наличие данных в БД."""
        self.sql_object.existence_check(customer, sql_register)
        if self.sql_object.check.DATE_START == self.period['DATE_START'].isoformat():
            msg = "Уже есть запись в БД по {0} (Регистр {1}, Дата_начало {2})".format(
                customer, sql_register, self.period['DATE_START'].isoformat())
            self.message.append(msg)
            return False
        else:
            self.period_id[sql_register] = self.sql_object.check.PERIOD_ID + 1
            return True

    def run_program(self):
        """
        Метод запускает основную программу.

        1. Создание соединения.
        2. Обход блока полученных настроек
        2.1. Очистка директроии загрузки
        2.2. Определение наличия записи в БД
        2.3. Создание объекта Cystomer
        2.4. Запуск парсера для получения отсутствующего в БД регистра
        2.5. Формирования блока программных сообщений
        3. Закрытие соедниения
        """
        self.sql_object.create_connection()
        for setting in self.settings_list:
            cleaner(path=setting['FILE']['BASE_DIR'])
            customer = setting['FILE']['SQL_NAME']
            ss = self.register_status_check(customer, 'SALES')
            rs = self.register_status_check(customer, 'RESTS')
            customer_prog = Customer(setting, self.period, self.period_id)
            if ss and rs:
                customer_prog.run_program('ALL')
                if customer_prog.file.sales_list:
                    self.sql_object.insert_values(customer_prog.file.sales_list)
                if customer_prog.file.rests_list:
                    self.sql_object.insert_values(customer_prog.file.rests_list)
            elif ss and not rs:
                customer_prog.run_program('SALES')
                if customer_prog.file.sales_list:
                    self.sql_object.insert_values(customer_prog.file.sales_list)
                msg = "Данные по остаткам уже загружены {0} ({1})".format(
                    setting['FILE']['SQL_NAME'], self.period_id['RESTS']
                )
            elif rs and not ss:
                customer_prog.run_program('RESTS')
                if customer_prog.file.rests_list:
                    self.sql_object.insert_values(customer_prog.file.rests_list)
                msg = "Данные по продажам уже загружены {0} ({1})".format(
                    setting['FILE']['SQL_NAME'], self.period_id['SALES']
                )
            else:
                msg = "Данные по {0} уже загружены в БД (НомерПериода='{1},{2}')".format(
                    setting['FILE']['SQL_NAME'], self.period_id['SALES'], self.period_id['RESTS']
                )
                self.message.append(msg)
            self.message += customer_prog.message
        self.sql_object.close_connection()
