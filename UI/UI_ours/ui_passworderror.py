# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'passworderror.ui'
#
# Created: Wed Jul 04 08:26:43 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_passworderror(object):
    def setupUi(self, passworderror):
        passworderror.setObjectName(_fromUtf8("passworderror"))
        passworderror.resize(400, 150)
        self.labelblank = QtGui.QLabel(passworderror)
        self.labelblank.setGeometry(QtCore.QRect(0, 0, 5, 30))
        self.labelblank.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelblank.setText(_fromUtf8(""))
        self.labelblank.setObjectName(_fromUtf8("labelblank"))
        self.labelicon = QtGui.QLabel(passworderror)
        self.labelicon.setGeometry(QtCore.QRect(5, 0, 30, 30))
        self.labelicon.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelicon.setText(_fromUtf8(""))
        self.labelicon.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/icon.png")))
        self.labelicon.setScaledContents(True)
        self.labelicon.setObjectName(_fromUtf8("labelicon"))
        self.labelerror = QtGui.QLabel(passworderror)
        self.labelerror.setGeometry(QtCore.QRect(35, 0, 365, 30))
        self.labelerror.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);\n"
"font: 12pt \"SimSun\"; \n"
"color: rgb(255, 255, 255);"))
        self.labelerror.setObjectName(_fromUtf8("labelerror"))
        self.labeltxt = QtGui.QLabel(passworderror)
        self.labeltxt.setGeometry(QtCore.QRect(0, 65, 400, 20))
        self.labeltxt.setObjectName(_fromUtf8("labeltxt"))
        self.buttonconfirm = QtGui.QPushButton(passworderror)
        self.buttonconfirm.setGeometry(QtCore.QRect(314, 120, 75, 23))
        self.buttonconfirm.setObjectName(_fromUtf8("buttonconfirm"))
        self.buttoncancel = QtGui.QPushButton(passworderror)
        self.buttoncancel.setGeometry(QtCore.QRect(360, 2, 31, 23))
        self.buttoncancel.setStyleSheet(_fromUtf8("border:outset"))
        self.buttoncancel.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon)
        self.buttoncancel.setObjectName(_fromUtf8("buttoncancel"))

        self.retranslateUi(passworderror)
        QtCore.QMetaObject.connectSlotsByName(passworderror)

    def retranslateUi(self, passworderror):
        passworderror.setWindowTitle(QtGui.QApplication.translate("passworderror", "passworderror", None, QtGui.QApplication.UnicodeUTF8))
        self.labelerror.setText(QtGui.QApplication.translate("passworderror", "错误", None, QtGui.QApplication.UnicodeUTF8))
        self.labeltxt.setText(QtGui.QApplication.translate("passworderror", " 您输入的密码错误，请重新输入", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonconfirm.setText(QtGui.QApplication.translate("passworderror", "确定", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
