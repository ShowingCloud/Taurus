#!/usr/bin/python

from PySide import QtGui, QtCore

from Frontend import MainWindow

app = QtGui.QApplication ([])
m = MainWindow (0, 0, 0, "", "", "", "", "")
m.show()
app.exec_()
