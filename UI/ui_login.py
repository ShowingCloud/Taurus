# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created: Thu Jun  7 18:11:13 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(461, 263)
        Login.setStyleSheet("background-color: rgb(102, 102, 102);")
        self.labelcpid = QtGui.QLabel(Login)
        self.labelcpid.setGeometry(QtCore.QRect(96,102, 57, 48))
        self.labelcpid.setStyleSheet("background-color: rgb(54, 54, 54);"
"font: 12pt \"SimHei\"; "
"color: rgb(102, 102, 102);"
"border-top-left-radius: 5px; "
"border-top-right-radius: 0px;"
"border-bottom-left-radius: 0px")
        self.labelcpid.setObjectName("labelcpid")
        self.labelpassword = QtGui.QLabel(Login)
        self.labelpassword.setGeometry(QtCore.QRect(96, 152, 57, 51))
        self.labelpassword.setStyleSheet("background-color: rgb(54, 54, 54);"
"font: 12pt \"SimHei\"; "
"color: rgb(102, 102, 102);"
"border-bottom-left-radius: 5px; "
"border-top-left-radius:0px")
        self.labelpassword.setObjectName("labelpassword")
        self.buttoncancel = QtGui.QPushButton(Login)
        self.buttoncancel.setGeometry(QtCore.QRect(424, 10, 25, 33))
        self.buttoncancel.setStyleSheet("border-style:outset; ")
        self.buttoncancel.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon)
        self.buttoncancel.setIconSize(QtCore.QSize(30, 30))
        self.buttoncancel.setObjectName("buttoncancel")
        self.lineeditcpid = QtGui.QLineEdit(Login)
        self.lineeditcpid.setGeometry(QtCore.QRect(152, 102, 205, 48))
        self.lineeditcpid.setStyleSheet("background-color: rgb(54, 54, 54);"
"border-style:outset; "
"color: rgb(102, 102, 102);"
"font: 12pt \"SimHei\"; "
"border-top-right-radius: 5px; ")
        self.lineeditcpid.setObjectName("lineeditcpid")
        self.lineeditpassword = QtGui.QLineEdit(Login)
        self.lineeditpassword.setGeometry(QtCore.QRect(152, 152, 205, 51))
        self.lineeditpassword.setStyleSheet("background-color: rgb(54, 54, 54);"
"border-style:outset; "
"color: rgb(102, 102, 102);"
"font: 12pt \"SimHei\"; "
"border-bottom-right-radius: 5px")
        self.lineeditpassword.setObjectName("lineeditpassword")
        self.labelcartoonupload = QtGui.QLabel(Login)
        self.labelcartoonupload.setGeometry(QtCore.QRect(137, 42, 231, 27))
        self.labelcartoonupload.setStyleSheet("color: rgb(214, 214, 214); "
"font: 75 20pt \"SimHei\";")
        self.labelcartoonupload.setObjectName("labelcartoonupload")
        self.labelcartoon = QtGui.QLabel(Login)
        self.labelcartoon.setGeometry(QtCore.QRect(84, 30, 51, 47))
        self.labelcartoon.setText("")
        self.labelcartoon.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.labelcartoon.setScaledContents(True)
        self.labelcartoon.setObjectName("labelcartoon")
        self.labelchinamoblie = QtGui.QLabel(Login)
        self.labelchinamoblie.setGeometry(QtCore.QRect(324, 210, 121, 45))
        self.labelchinamoblie.setText("")
        self.labelchinamoblie.setPixmap(QtGui.QPixmap(":/images/China Mobile icon.png"))
        self.labelchinamoblie.setScaledContents(True)
        self.labelchinamoblie.setObjectName("labelchinamoblie")
        self.buttonforgetpassword = QtGui.QPushButton(Login)
        self.buttonforgetpassword.setGeometry(QtCore.QRect(96, 211, 73, 15))
        self.buttonforgetpassword.setStyleSheet("border-style:outset; "
"font: 9pt \"Adobe Arabic\"; "
"color: rgb(214, 214, 214);"
"text-decoration: underline;")
        self.buttonforgetpassword.setObjectName("buttonforgetpassword")
        self.label = QtGui.QLabel(Login)
        self.label.setGeometry(QtCore.QRect(96, 142, 7, 17))
        self.label.setStyleSheet("background-color: rgb(54, 54, 54);")
        self.label.setText("")
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Login)
        self.label_2.setGeometry(QtCore.QRect(320, 140,7, 25))
        self.label_2.setStyleSheet("background-color: rgb(54, 54, 54);")
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.buttonaccept = QtGui.QPushButton(Login)
        self.buttonaccept.setGeometry(QtCore.QRect(326, 120, 61, 63))
        self.buttonaccept.setStyleSheet("border-style:outset; "
"background-color: rgba(255, 255, 255, 0);")
        self.buttonaccept.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/login2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonaccept.setIcon(icon1)
        self.buttonaccept.setIconSize(QtCore.QSize(90, 90))
        self.buttonaccept.setObjectName("buttonaccept")

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        Login.setWindowTitle(QtGui.QApplication.translate("Login", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.labelcpid.setText(QtGui.QApplication.translate("Login", " CP帐号", None, QtGui.QApplication.UnicodeUTF8))
        self.labelpassword.setText(QtGui.QApplication.translate("Login", " 密 码", None, QtGui.QApplication.UnicodeUTF8))
        self.labelcartoonupload.setText(QtGui.QApplication.translate("Login", "动画编码上传平台", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonforgetpassword.setText(QtGui.QApplication.translate("Login", "忘记密码？", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
