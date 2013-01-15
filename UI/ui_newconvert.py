# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newconvert.ui'
#
# Created: Mon Jun 25 16:53:39 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_newconvert(object):
    def setupUi(self, newconvert):
        newconvert.setObjectName("newconvert")
        newconvert.resize(461, 451)
        newconvert.setStyleSheet("background-color: rgb(221, 227, 255);")
        self.groupBox = QtGui.QGroupBox(newconvert)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 468, 30))
        self.groupBox.setStyleSheet("background-color: rgb(153, 153, 153);\n"
"border:outset")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.labelnewconvertmission = QtGui.QLabel(self.groupBox)
        self.labelnewconvertmission.setGeometry(QtCore.QRect(188, 9, 113, 16))
        self.labelnewconvertmission.setStyleSheet("font: 10pt \"黑体\";\n"
"color: rgb(255, 255, 255);")
        self.labelnewconvertmission.setObjectName("labelnewconvertmission")
        self.labeloutputroute = QtGui.QLabel(newconvert)
        self.labeloutputroute.setGeometry(QtCore.QRect(20, 46, 59, 16))
        self.labeloutputroute.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.labeloutputroute.setObjectName("labeloutputroute")
        self.buttonbrowse = QtGui.QPushButton(newconvert)
        self.buttonbrowse.setGeometry(QtCore.QRect(350, 40, 68, 23))
        self.buttonbrowse.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.buttonbrowse.setObjectName("buttonbrowse")
        self.lineeditoutputroute = QtGui.QLineEdit(newconvert)
        self.lineeditoutputroute.setGeometry(QtCore.QRect(90, 42, 250, 24))
        self.lineeditoutputroute.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineeditoutputroute.setObjectName("lineeditoutputroute")
        self.groupBox_2 = QtGui.QGroupBox(newconvert)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 74, 435, 325))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.labelconvertlist = QtGui.QLabel(self.groupBox_2)
        self.labelconvertlist.setGeometry(QtCore.QRect(0, 0, 126, 32))
        self.labelconvertlist.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(112,112, 112, 255), stop:1 rgba(200,200,200, 255));\n"
"color: rgb(255, 255, 255);")
        self.labelconvertlist.setObjectName("labelconvertlist")
        self.groupBox_3 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_3.setGeometry(QtCore.QRect(126, 0, 309, 33))
        self.groupBox_3.setStyleSheet("border:outset;\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(108,108,108, 255), stop:1 rgba(26,26,26, 255));\n"
"")
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.buttonplus = QtGui.QPushButton(self.groupBox_3)
        self.buttonplus.setGeometry(QtCore.QRect(254, 2, 29, 27))
        self.buttonplus.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.buttonplus.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplus.setIcon(icon)
        self.buttonplus.setIconSize(QtCore.QSize(27, 27))
        self.buttonplus.setObjectName("buttonplus")
        self.tableWidget = QtGui.QTableWidget(self.groupBox_2)
        self.tableWidget.setGeometry(QtCore.QRect(0, 32, 435, 293))
        self.tableWidget.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(232, 232, 232, 255), stop:1 rgba(137,137, 137, 255));\n"
"border-top:outset;")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.groupBox_4 = QtGui.QGroupBox(newconvert)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 408, 461, 43))
        self.groupBox_4.setStyleSheet("background-color: rgb(153, 153, 153);\n"
"border:outset\n"
"")
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.buttonconvert = QtGui.QPushButton(self.groupBox_4)
        self.buttonconvert.setGeometry(QtCore.QRect(307, 9, 68, 31))
        self.buttonconvert.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/convert.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonconvert.setIcon(icon1)
        self.buttonconvert.setIconSize(QtCore.QSize(68, 28))
        self.buttonconvert.setObjectName("buttonconvert")
        self.buttoncancel = QtGui.QPushButton(self.groupBox_4)
        self.buttoncancel.setGeometry(QtCore.QRect(380, 9, 68, 31))
        self.buttoncancel.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon2)
        self.buttoncancel.setIconSize(QtCore.QSize(68, 28))
        self.buttoncancel.setObjectName("buttoncancel")

        self.retranslateUi(newconvert)
        QtCore.QMetaObject.connectSlotsByName(newconvert)

    def retranslateUi(self, newconvert):
        newconvert.setWindowTitle(QtGui.QApplication.translate("newconvert", "newconvert", None, QtGui.QApplication.UnicodeUTF8))
        self.labelnewconvertmission.setText(QtGui.QApplication.translate("newconvert", "新建转换任务", None, QtGui.QApplication.UnicodeUTF8))
        self.labeloutputroute.setText(QtGui.QApplication.translate("newconvert", "输出路径：", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonbrowse.setText(QtGui.QApplication.translate("newconvert", "浏览", None, QtGui.QApplication.UnicodeUTF8))
        self.labelconvertlist.setText(QtGui.QApplication.translate("newconvert", "      转换列表", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
