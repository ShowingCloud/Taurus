# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newconvert(1).ui'
#
# Created: Sun Jul 01 23:50:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_newconvert(object):
    def setupUi(self, newconvert):
        newconvert.setObjectName(_fromUtf8("newconvert"))
        newconvert.resize(461, 451)
        newconvert.setStyleSheet(_fromUtf8("background-color: rgb(221, 227, 255);"))
        self.labeloutputroute = QtGui.QLabel(newconvert)
        self.labeloutputroute.setGeometry(QtCore.QRect(20, 46, 59, 16))
        self.labeloutputroute.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);"))
        self.labeloutputroute.setObjectName(_fromUtf8("labeloutputroute"))
        self.buttonbrowse = QtGui.QPushButton(newconvert)
        self.buttonbrowse.setGeometry(QtCore.QRect(350, 40, 68, 23))
        self.buttonbrowse.setStyleSheet(_fromUtf8("\n"
"\n"
"QPushButton{\n"
"border-right-color: rgb(105, 105, 105);\n"
"border-bottom-color: rgb(105, 105, 105);\n"
"border-width:2px;\n"
"background-color: rgb(242, 242, 242);\n"
"border-style:inset;\n"
"border-top-color: rgb(255, 255, 255);\n"
"border-left-color: rgb(255, 255, 255);}\n"
"QPushButton::pressed {border-bottom-color: rgb(255, 255, 255);\n"
"border-width:2px;\n"
"background-color: rgb(242, 242, 242);\n"
"border-style:ridge;\n"
"border-top-color: rgb(105, 105, 105);\n"
"border-left-color: rgb(105, 105, 105);\n"
"border-right-color: rgb(255, 255, 255);\n"
"}\n"
"\n"
""))
        self.buttonbrowse.setObjectName(_fromUtf8("buttonbrowse"))
        self.lineeditoutputroute = QtGui.QLineEdit(newconvert)
        self.lineeditoutputroute.setGeometry(QtCore.QRect(90, 42, 250, 24))
        self.lineeditoutputroute.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255); \n"
"border-right-color: rgb(255, 255, 255);\n"
"border-bottom-color: rgb(255, 255, 255);\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-top-color: rgb(105, 105, 105);\n"
"border-left-color: rgb(105, 105, 105);"))
        self.lineeditoutputroute.setObjectName(_fromUtf8("lineeditoutputroute"))
        self.groupBox_2 = QtGui.QGroupBox(newconvert)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 74, 435, 325))
        self.groupBox_2.setTitle(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.labelconvertlist = QtGui.QLabel(self.groupBox_2)
        self.labelconvertlist.setGeometry(QtCore.QRect(0, 0, 126, 32))
        self.labelconvertlist.setStyleSheet(_fromUtf8("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(112,112, 112, 255), stop:1 rgba(200,200,200, 255));\n"
"color: rgb(255, 255, 255);\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-bottom-style:none;\n"
"border-right-style:none;\n"
"border-left-color: rgb(102, 102, 102);\n"
"border-top-color: rgb(102, 102, 102);"))
        self.labelconvertlist.setObjectName(_fromUtf8("labelconvertlist"))
        self.groupBox_3 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_3.setGeometry(QtCore.QRect(126, 0, 309, 33))
        self.groupBox_3.setStyleSheet(_fromUtf8("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(108,108,108, 255), stop:1 rgba(26,26,26, 255));\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-bottom-style:none;\n"
"border-left-style:none;\n"
"border-top-color: rgb(102, 102, 102);\n"
"border-right-color: rgb(102, 102, 102);"))
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.buttonplus = QtGui.QPushButton(self.groupBox_3)
        self.buttonplus.setGeometry(QtCore.QRect(254, 2, 29, 27))
        self.buttonplus.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"border:outset;"))
        self.buttonplus.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/convertplus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplus.setIcon(icon)
        self.buttonplus.setIconSize(QtCore.QSize(27, 27))
        self.buttonplus.setObjectName(_fromUtf8("buttonplus"))
        self.treeView = QtGui.QTreeView(self.groupBox_2)
        self.treeView.setGeometry(QtCore.QRect(0, 32, 435, 293))
        self.treeView.setStyleSheet(_fromUtf8("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(232, 232, 232, 255), stop:1 rgba(137,137, 137, 255));\n"
"border-left-color: rgb(102, 102, 102);\n"
"border-bottom-color: rgb(102, 102, 102);\n"
"border-right-color: rgb(102, 102, 102);\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-top-style:none"))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.groupBox_4 = QtGui.QGroupBox(newconvert)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 408, 461, 43))
        self.groupBox_4.setStyleSheet(_fromUtf8("background-color: rgb(153, 153, 153);\n"
"border:outset\n"
""))
        self.groupBox_4.setTitle(_fromUtf8(""))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.buttonconvert = QtGui.QPushButton(self.groupBox_4)
        self.buttonconvert.setGeometry(QtCore.QRect(307, 9, 68, 31))
        self.buttonconvert.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/convertconvert.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonconvert.setIcon(icon1)
        self.buttonconvert.setIconSize(QtCore.QSize(68, 28))
        self.buttonconvert.setObjectName(_fromUtf8("buttonconvert"))
        self.buttoncancel = QtGui.QPushButton(self.groupBox_4)
        self.buttoncancel.setGeometry(QtCore.QRect(380, 9, 68, 31))
        self.buttoncancel.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/convertcancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon2)
        self.buttoncancel.setIconSize(QtCore.QSize(68, 28))
        self.buttoncancel.setObjectName(_fromUtf8("buttoncancel"))
        self.label = QtGui.QLabel(newconvert)
        self.label.setGeometry(QtCore.QRect(0, 0, 184, 30))
        self.label.setStyleSheet(_fromUtf8("background-color: rgb(153, 153, 153);"))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(newconvert)
        self.label_2.setGeometry(QtCore.QRect(276, 0, 185, 30))
        self.label_2.setStyleSheet(_fromUtf8("background-color: rgb(153, 153, 153);"))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.labelnewconvertmission = QtGui.QLabel(newconvert)
        self.labelnewconvertmission.setGeometry(QtCore.QRect(184, 0, 92, 30))
        self.labelnewconvertmission.setStyleSheet(_fromUtf8("font: bold 10pt \"SimHei\";\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(153, 153, 153);"))
        self.labelnewconvertmission.setObjectName(_fromUtf8("labelnewconvertmission"))

        self.retranslateUi(newconvert)
        QtCore.QMetaObject.connectSlotsByName(newconvert)

    def retranslateUi(self, newconvert):
        newconvert.setWindowTitle(QtGui.QApplication.translate("newconvert", "newconvert", None, QtGui.QApplication.UnicodeUTF8))
        self.labeloutputroute.setText(QtGui.QApplication.translate("newconvert", "输出路径：", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonbrowse.setText(QtGui.QApplication.translate("newconvert", "浏览", None, QtGui.QApplication.UnicodeUTF8))
        self.labelconvertlist.setText(QtGui.QApplication.translate("newconvert", "      转换列表", None, QtGui.QApplication.UnicodeUTF8))
        self.labelnewconvertmission.setText(QtGui.QApplication.translate("newconvert", "新建转换任务", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
