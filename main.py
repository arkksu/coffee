from sys import argv, exit
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('main.ui', self)
        self.dbcon = sqlite3.connect('coffee.sqlite')
        self.setWindowTitle('coffee')
        self.editbutton.clicked.connect(self.edit_event)
        self.show_data()

    def show_data(self) -> None:
        data = self.dbcon.cursor().execute("SELECT * FROM coffee").fetchall()
        self.maintable.setRowCount(len(data))
        self.maintable.setColumnCount(len(data[0]))
        self.maintable.setHorizontalHeaderLabels(['id', 'Название', 'Страна', 'Описание', 'Цена'])
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.maintable.setItem(i, j, QTableWidgetItem(str(val)))

    def edit_event(self) -> None:
        self.editw = EditWidget(parent=self)
        self.editw.exec()

    def closeEvent(self, event) -> None:
        self.dbcon.close()
        QApplication.closeAllWindows()


class EditWidget(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.parent = parent
        self.current = self.addradio
        self.addradio.clicked.connect(self.check_radio)
        self.editradio.clicked.connect(self.check_radio)
        self.idbutton.clicked.connect(self.load_event)
        self.cancelbutton.clicked.connect(self.close_event)
        self.savebutton.clicked.connect(self.save_event)

    def check_radio(self) -> None:
        if self.addradio.isChecked():
            self.current = self.addradio
            self.idedit.setEnabled(False)
            self.idbutton.setEnabled(False)
        elif self.editradio.isChecked():
            self.current = self.editradio
            self.idedit.setEnabled(True)
            self.idbutton.setEnabled(True)

    def load_event(self) -> None:
        try:
            data = self.parent.dbcon.cursor().execute(
                f'SELECT * FROM coffee WHERE id = {self.idedit.text()}').fetchone()
            self.name.setText(data[1])
            self.country.setText(data[2])
            self.desc.setPlainText(data[3])
            self.price.setText(str(data[4]))
        except sqlite3.IntegrityError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle('Ошибка')
            msg.setText('В базе данных нет записей с данным id')
            msg.exec()

    def close_event(self) -> None:
        self.close()

    def save_event(self) -> None:
        if not self.name.text():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle('Ошибка')
            msg.setText('Название не может быть пустым')
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle('Изменение данных')
            msg.setText(f'Вы уверены, что хотите добавить/изменить данные?')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            answer = msg.exec()
            if answer == QMessageBox.Yes:
                name = self.name.text()
                country = self.country.text()
                if not country:
                    country = 'NULL'
                desc = self.desc.toPlainText()
                if not desc:
                    desc = 'NULL'
                try:
                    price = float(self.price.text())
                    if self.current == self.addradio:
                        data = self.parent.dbcon.cursor().execute(f'SELECT sort FROM coffee').fetchall()
                        f = True
                        for elem in data:
                            if elem[0] == self.name.text():
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Critical)
                                msg.setWindowTitle('Ошибка')
                                msg.setText('Название должно быть уникальным')
                                msg.exec()
                                f = False
                                break
                        if f:
                            self.parent.dbcon.cursor().execute(f'''INSERT INTO coffee (sort, country, description,
                                price) VALUES ("{name}", "{country}", "{desc}", {price})''')
                    else:
                        self.parent.dbcon.cursor().execute(f'''UPDATE coffee SET sort = "{name}",
                                                        country = "{country}", description = "{desc}", price = {price}
                                                        WHERE id = {self.idedit.text()}''')
                    self.parent.dbcon.commit()
                    self.parent.show_data()
                    self.close_event()
                except ValueError:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle('Ошибка')
                    msg.setText('Поле с ценой должно быть числом')
                    msg.exec()


if __name__ == '__main__':
    app = QApplication(argv)
    window = MyWidget()
    window.show()
    exit(app.exec())
