# Monday-customer-report
Weekly monday sales / rests report by main customers

1. Авторизация в личном кабинете поставщика
2. Выгрука отчетов по продажам и остаткам
3. Парсинг файлов с xml таблицами отчетов
4. Загрука данных в базу данных MS SQL

Используемые внешние библиотеки:
selenium - управление драйвером chromedriver.exe
pyodbc - управление загрузкой данных в MS SQL
bs4 - парсинг xml файла через объект BeautifulSoup

Используемые внутренние бибилиотеки:
datetime, copy, itertools, collections

Программа разделена на следующие модули:
driver_object - содержит класс Driver для управления chromedriver.exe;
sql_object - содержит класс Sql для управления обемном данных с MS SQL;
parser_object - содержит класс BaseParser и производные ParserTypeOne, ParserTypeTwo описывающих обход личного кабинета контрагента;
decorator - содержит параметризованные декораторы для обработки загруки url и тегов DOM;
customer_object - содержит класс BaseCustomer и производные классы для каждого контрагента. Модуль масштабируемый. Для добавления новых контрагентов достаточно создать класс наследуемый от BaseCustomer, добавить его в CLASS_LIST и сформировать соответсвующий блок настроек;
file_object - содержит класс File, отвечабщий за обработку выгруженных файлов и формирование массивов данных для загрузки в БД;
main - содержит стартовую функцию main() запускающую полный цикл программы для всех контрагентов списка CLASS_LIST

Для каждого контрагента предусмотрена своя директория выгрузки файлов и модуля настроек.
Модуль настроек иммет детальную информацию для всех программных модулей. Это обеспечивает удобные корректировки в случае изменения исходных данных: логина, пароля, url ключевых страниц, обрабатываемых тегов DOM, структуры отчетных файлов, параметров БД;
    


