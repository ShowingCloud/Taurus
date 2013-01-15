# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginlist.ui'
#
# Created: Mon Jun 25 16:53:09 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_loginlist(object):
    def setupUi(self, loginlist):
        loginlist.setObjectName("loginlist")
        loginlist.resize(461, 263)
        loginlist.setStyleSheet("background-color: rgb(102, 102, 102);")
        self.labelcartoon = QtGui.QLabel(loginlist)
        self.labelcartoon.setGeometry(QtCore.QRect(84, 30, 51, 47))
        self.labelcartoon.setText("")
        self.labelcartoon.setPixmap(QtGui.QPixmap(":/images/icon.png"))
        self.labelcartoon.setScaledContents(True)
        self.labelcartoon.setObjectName("labelcartoon")
        self.labelcartoonupload = QtGui.QLabel(loginlist)
        self.labelcartoonupload.setGeometry(QtCore.QRect(137, 42, 231, 27))
        self.labelcartoonupload.setStyleSheet("color: rgb(214, 214, 214); font: 75 20pt \"SimHei\";")
        self.labelcartoonupload.setObjectName("labelcartoonupload")
        self.progressBar = QtGui.QProgressBar(loginlist)
        self.progressBar.setGeometry(QtCore.QRect(70, 140, 349, 25))
#        self.progressBar.setStyleSheet(" QProgressBar {border-radius: 5px;}"
#"QProgressBar::chunk {background-color: black; width: 5px;}"
#"QProgressBar {background-color:rgb(255, 255, 255); border-radius: 5px; text-align: center;}")
        self.progressBar.setStyleSheet(" QProgressBar {border-radius: 5px;}"
                                       "QProgressBar::chunk {background-color: #19d73d;"
                                       "width: 5px;}"
                                       "QProgressBar {background-color:rgb(255, 255, 255); "
                                       "border-radius: 5px; text-align: center;}")
        self.progressBar.setMinimum(0)
        self.progressBar.setProperty("value", 13)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.label = QtGui.QLabel(loginlist)
        self.label.setGeometry(QtCore.QRect(150, 119, 161, 17))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        self.label.setObjectName("label")
        self.pushButton = QtGui.QPushButton(loginlist)
        self.pushButton.setGeometry(QtCore.QRect(420, 10, 25, 33))
        self.pushButton.setStyleSheet("border:outset;")
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(30, 30))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(loginlist)
        self.progressBar.setFocus()
        QtCore.QMetaObject.connectSlotsByName(loginlist)

    def retranslateUi(self, loginlist):
        loginlist.setWindowTitle(QtGui.QApplication.translate("loginlist", "loginlist", None, QtGui.QApplication.UnicodeUTF8))
        self.labelcartoonupload.setText(QtGui.QApplication.translate("loginlist", "动画编码上传平台", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("loginlist", "正在同步配置列表...", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
