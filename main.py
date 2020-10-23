# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from ui import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
