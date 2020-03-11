"""Модуль содержит основной интрефейс программы."""
import datetime
from PyQt5 import QtWidgets
from program_object import Program
from settings import sql_settings, customer_settings


class MyWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.label_start = QtWidgets.QLabel('Дата начала (дд.мм.гггг): ')
        self.date_start = QtWidgets.QDateEdit(datetime.date.today() - datetime.timedelta(days=7))
        self.label_end = QtWidgets.QLabel('Дата окончания (дд.мм.гггг): ')
        self.date_end = QtWidgets.QDateEdit(datetime.date.today())
        self.button = QtWidgets.QPushButton('Запустить программу')
        self.message = QtWidgets.QTextBrowser()
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.label_start)
        self.vbox.addWidget(self.date_start)
        self.vbox.addWidget(self.label_end)
        self.vbox.addWidget(self.date_end)
        self.vbox.addWidget(self.button)
        self.vbox.addWidget(self.message)
        self.setLayout(self.vbox)
        self.button.clicked.connect(self.run_program)
        # self.pattern = re.compile('^[0-3][0-9].[01][0-9].[2][0][12][0-9]$')

    def run_program(self):
        """
        Метод при нажатии на кнопку запуска программы.

        1. Формирование dict() period и проверка правильности дат
        2. Создание объекта Program и запуск основного модуля
        3. Формирования блока программных сообщений и вывод в TextBrowser
        """
        self.message.clear()
        period = {
            'DATE_START': datetime.date(*self.date_start.date().getDate()),
            'DATE_END': datetime.date(*self.date_end.date().getDate())
        }
        if period['DATE_START'] >= period['DATE_END']:
            self.message.setText('ОШИБКА ВВОДА ДАТЫ. ДАТА НАЧАЛА БОЛЬШЕ ДАТЫ ОКОНЧАНИЯ')
        else:
            self.button.setDisabled(True)
            program = Program(period, sql_settings, customer_settings)
            program.run_program()
            for msg in program.message:
                self.message.append(msg + '\n')
            self.button.setEnabled(True)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.resize(350, 300)
    window.show()
    sys.exit(app.exec_())