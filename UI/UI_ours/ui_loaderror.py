# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loaderror.ui'
#
# Created: Wed Jul 04 08:26:26 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_loaderror(object):
    def setupUi(self, loaderror):
        loaderror.setObjectName(_fromUtf8("loaderror"))
        loaderror.resize(400, 150)
        self.labelblank = QtGui.QLabel(loaderror)
        self.labelblank.setGeometry(QtCore.QRect(0, 0, 5, 30))
        self.labelblank.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelblank.setText(_fromUtf8(""))
        self.labelblank.setObjectName(_fromUtf8("labelblank"))
        self.labelicon = QtGui.QLabel(loaderror)
        self.labelicon.setGeometry(QtCore.QRect(5, 0, 30, 30))
        self.labelicon.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelicon.setText(_fromUtf8(""))
        self.labelicon.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/icon.png")))
        self.labelicon.setScaledContents(True)
        self.labelicon.setObjectName(_fromUtf8("labelicon"))
        self.labelerror = QtGui.QLabel(loaderror)
        self.labelerror.setGeometry(QtCore.QRect(35, 0, 365, 30))
        self.labelerror.setStyleSheet(_fromUtf8("font: 12pt \"SimSun\"; \n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(81, 81, 81);"))
        self.labelerror.setObjectName(_fromUtf8("labelerror"))
        self.labeltxt = QtGui.QLabel(loaderror)
        self.labeltxt.setGeometry(QtCore.QRect(0, 65, 400, 20))
        self.labeltxt.setObjectName(_fromUtf8("labeltxt"))
        self.buttonload = QtGui.QPushButton(loaderror)
        self.buttonload.setGeometry(QtCore.QRect(28, 110, 347, 23))
        self.buttonload.setStyleSheet(_fromUtf8("border:outset;\n"
"color: rgb(0, 0, 255);\n"
"text-decoration: underline;"))
        self.buttonload.setObjectName(_fromUtf8("buttonload"))
        self.buttoncancel = QtGui.QPushButton(loaderror)
        self.buttoncancel.setGeometry(QtCore.QRect(350, 2, 29, 23))
        self.buttoncancel.setStyleSheet(_fromUtf8("border:outset;"))
        self.buttoncancel.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon)
        self.buttoncancel.setObjectName(_fromUtf8("buttoncancel"))

        self.retranslateUi(loaderror)
        QtCore.QMetaObject.connectSlotsByName(loaderror)

    def retranslateUi(self, loaderror):
        loaderror.setWindowTitle(QtGui.QApplication.translate("loaderror", "loaderror", None, QtGui.QApplication.UnicodeUTF8))
        self.labelerror.setText(QtGui.QApplication.translate("loaderror", "错误", None, QtGui.QApplication.UnicodeUTF8))
        self.labeltxt.setText(QtGui.QApplication.translate("loaderror", "      对不起，您导入的视频文件未满足源视频参数标准，无法导入！", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonload.setText(QtGui.QApplication.translate("loaderror", "查阅源视频文件导入标准", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
