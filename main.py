"""Модуль содекжит функцию main()."""
import datetime
from itertools import count
from customer_object import CLASS_LIST
from cleaner_object import cleaner
from sql_object import Sql
from settings import SQL


def main():
    """
    Функция запускает программу выгрузки отчетов и их записи в БД.

    1. Объявление глобального счетчика
    2. Объявление период отчета
    3. Создание объекта SQL
    4. Создание подключения к БД
    5. Получение ID периода для периода отчета
    6. Поочередное создание объектов блока customer_object
    7. Очиска директории выгруки файлов
    8. Запуск процедуры выгрузки отчетов из ЛК
    9. Обработка файлов и запись данных в БД
    10. Закрытие соединения с БД
    """
    counter = count(0)
    period = {
        'DATE_START': datetime.date(2020, 2, 17),
        'DATE_END': datetime.date(2020, 2, 23)
    }
    sql_object = Sql(SQL, counter)
    sql_object.create_connection()
    sql_object.get_period_id()
    if sql_object.period_id:
        for cls in CLASS_LIST:
            program_object = cls(period=period, counter=counter, period_id=sql_object.period_id)
            cleaner(program_object.__class__.SETTINGS['FILE']['BASE_DIR'])
            program_object.run_program()
            if program_object.file.sales_list:
                sql_object.insert_values(program_object.file.sales_list)
            if program_object.file.rests_list:
                sql_object.insert_values(program_object.file.rests_list)
    sql_object.close_connection()


if __name__ == '__main__':
    main()
