# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mergererror.ui'
#
# Created: Wed Jul 04 08:24:14 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_mergererror(object):
    def setupUi(self, mergererror):
        mergererror.setObjectName(_fromUtf8("mergererror"))
        mergererror.resize(400, 150)
        self.labelblank = QtGui.QLabel(mergererror)
        self.labelblank.setGeometry(QtCore.QRect(0, 0, 5, 30))
        self.labelblank.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelblank.setText(_fromUtf8(""))
        self.labelblank.setObjectName(_fromUtf8("labelblank"))
        self.labelerror = QtGui.QLabel(mergererror)
        self.labelerror.setGeometry(QtCore.QRect(5, 0, 30, 30))
        self.labelerror.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelerror.setText(_fromUtf8(""))
        self.labelerror.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/icon.png")))
        self.labelerror.setScaledContents(True)
        self.labelerror.setObjectName(_fromUtf8("labelerror"))
        self.labelerror_2 = QtGui.QLabel(mergererror)
        self.labelerror_2.setGeometry(QtCore.QRect(35, 0, 365, 30))
        self.labelerror_2.setStyleSheet(_fromUtf8("font: 12pt \"SimSun\"; \n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(81, 81, 81);"))
        self.labelerror_2.setObjectName(_fromUtf8("labelerror_2"))
        self.buttonconfirm = QtGui.QPushButton(mergererror)
        self.buttonconfirm.setGeometry(QtCore.QRect(316, 122, 75, 23))
        self.buttonconfirm.setObjectName(_fromUtf8("buttonconfirm"))
        self.label_4 = QtGui.QLabel(mergererror)
        self.label_4.setGeometry(QtCore.QRect(0, 65, 400, 20))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.buttoncancel = QtGui.QPushButton(mergererror)
        self.buttoncancel.setGeometry(QtCore.QRect(346, 4, 27, 23))
        self.buttoncancel.setStyleSheet(_fromUtf8("border:outset;"))
        self.buttoncancel.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon)
        self.buttoncancel.setObjectName(_fromUtf8("buttoncancel"))

        self.retranslateUi(mergererror)
        QtCore.QMetaObject.connectSlotsByName(mergererror)

    def retranslateUi(self, mergererror):
        mergererror.setWindowTitle(QtGui.QApplication.translate("mergererror", "mergererror", None, QtGui.QApplication.UnicodeUTF8))
        self.labelerror_2.setText(QtGui.QApplication.translate("mergererror", "错误", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonconfirm.setText(QtGui.QApplication.translate("mergererror", "确定", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("mergererror", "对不起，您所提供的视频文件格式或参数不一致，无法合并", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
