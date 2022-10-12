import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 150, 150)
        self.setWindowTitle('Диалоговые окна')

        self.button_1 = QPushButton(self)
        self.button_1.move(20, 40)
        self.button_1.setText("Кнопка")
        self.button_1.clicked.connect(self.run)
        self.btn = QPushButton(self)
        self.btn.setText('Тест вывод')
        self.lbl = QLabel(self)
        self.lbl.move(100, 100)
        self.btn.clicked.connect(self.run_2)

    def run_2(self):
        pixmap = QPixmap(self.fname)
        self.lbl.setPixmap(pixmap)

    def run(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        print(self.fname)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())