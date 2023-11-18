from sys import argv, exit
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.dbcon = sqlite3.connect('coffee.sqlite')
        self.setWindowTitle('coffee')
        self.show_data()

    def show_data(self):
        data = self.dbcon.cursor().execute("SELECT * FROM coffee").fetchall()
        self.maintable.setRowCount(len(data))
        self.maintable.setColumnCount(len(data[0]))
        self.maintable.setHorizontalHeaderLabels(['id', 'Название', 'Страна', 'Описание', 'Цена'])
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.maintable.setItem(i, j, QTableWidgetItem(str(val)))

    def closeEvent(self, event):
        self.dbcon.close()
        QApplication.closeAllWindows()


if __name__ == '__main__':
    app = QApplication(argv)
    window = MyWidget()
    window.show()
    exit(app.exec())
