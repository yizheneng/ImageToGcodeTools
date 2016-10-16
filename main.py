from PyQt4 import QtGui
from mainwindows import MainWindow

if __name__ == "__main__":
    app = QtGui.QApplication([])
    m = MainWindow()
    m.show()
    app.exec_()