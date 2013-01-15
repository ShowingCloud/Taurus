# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forgetpassword.ui'
#
# Created: Wed Jul 04 08:40:48 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_forgetpassword(object):
    def setupUi(self, forgetpassword):
        forgetpassword.setObjectName(_fromUtf8("forgetpassword"))
        forgetpassword.resize(400, 150)
        self.labelblank = QtGui.QLabel(forgetpassword)
        self.labelblank.setGeometry(QtCore.QRect(0, 0, 5, 30))
        self.labelblank.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelblank.setText(_fromUtf8(""))
        self.labelblank.setObjectName(_fromUtf8("labelblank"))
        self.labelicon = QtGui.QLabel(forgetpassword)
        self.labelicon.setGeometry(QtCore.QRect(5, 0, 30, 30))
        self.labelicon.setStyleSheet(_fromUtf8("background-color: rgb(81, 81, 81);"))
        self.labelicon.setText(_fromUtf8(""))
        self.labelicon.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/icon.png")))
        self.labelicon.setScaledContents(True)
        self.labelicon.setObjectName(_fromUtf8("labelicon"))
        self.labelprompt = QtGui.QLabel(forgetpassword)
        self.labelprompt.setGeometry(QtCore.QRect(35, 0, 365, 30))
        self.labelprompt.setStyleSheet(_fromUtf8("font: 12pt \"SimSun\"; \n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(81, 81, 81);"))
        self.labelprompt.setObjectName(_fromUtf8("labelprompt"))
        self.buttonconfirm = QtGui.QPushButton(forgetpassword)
        self.buttonconfirm.setGeometry(QtCore.QRect(320, 124, 75, 23))
        self.buttonconfirm.setObjectName(_fromUtf8("buttonconfirm"))
        self.labeltxt = QtGui.QLabel(forgetpassword)
        self.labeltxt.setGeometry(QtCore.QRect(0, 65, 400, 20))
        self.labeltxt.setAlignment(QtCore.Qt.AlignCenter)
        self.labeltxt.setObjectName(_fromUtf8("labeltxt"))
        self.pushButton = QtGui.QPushButton(forgetpassword)
        self.pushButton.setGeometry(QtCore.QRect(364, 4, 27, 23))
        self.pushButton.setStyleSheet(_fromUtf8("border:outset"))
        self.pushButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(forgetpassword)
        QtCore.QMetaObject.connectSlotsByName(forgetpassword)

    def retranslateUi(self, forgetpassword):
        forgetpassword.setWindowTitle(QtGui.QApplication.translate("forgetpassword", "forgetpassword", None, QtGui.QApplication.UnicodeUTF8))
        self.labelprompt.setText(QtGui.QApplication.translate("forgetpassword", "提示", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonconfirm.setText(QtGui.QApplication.translate("forgetpassword", "确定", None, QtGui.QApplication.UnicodeUTF8))
        self.labeltxt.setText(QtGui.QApplication.translate("forgetpassword", "请拨打0592-XXXXXXXX或发送邮件到admin@139.com联系管理员修改密码", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
