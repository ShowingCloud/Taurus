# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'save.ui'
#
# Created: Mon Jun 25 16:48:06 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_save(object):
    def setupUi(self, save):
        save.setObjectName("save")
        save.resize(540, 152)
        save.setMinimumSize(QtCore.QSize(540, 152))
        save.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(242, 242, 242, 255), stop:1 rgba(153,153, 153, 255));")
        self.labelcartoonname = QtGui.QLabel(save)
        self.labelcartoonname.setGeometry(QtCore.QRect(14, 26, 101, 16))
        self.labelcartoonname.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";")
        self.labelcartoonname.setObjectName("labelcartoonname")
        self.labelsaveroute = QtGui.QLabel(save)
        self.labelsaveroute.setGeometry(QtCore.QRect(14, 60, 117, 16))
        self.labelsaveroute.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";")
        self.labelsaveroute.setObjectName("labelsaveroute")
        self.groupBox = QtGui.QGroupBox(save)
        self.groupBox.setGeometry(QtCore.QRect(0, 118, 543, 34))
        self.groupBox.setStyleSheet("background-color: rgb(153, 153, 153);\n"
"border:outset")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.buttonsave = QtGui.QPushButton(self.groupBox)
        self.buttonsave.setGeometry(QtCore.QRect(394, 4, 70, 26))
        self.buttonsave.setStyleSheet("background-color: rgba(255, 255, 255,0);\n"
"border:outset\n"
"\n"
"")
        self.buttonsave.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonsave.setIcon(icon)
        self.buttonsave.setIconSize(QtCore.QSize(68, 24))
        self.buttonsave.setObjectName("buttonsave")
        self.buttoncancel = QtGui.QPushButton(self.groupBox)
        self.buttoncancel.setGeometry(QtCore.QRect(466, 4, 70, 26))
        self.buttoncancel.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"border:outset")
        self.buttoncancel.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon1)
        self.buttoncancel.setIconSize(QtCore.QSize(66, 22))
        self.buttoncancel.setObjectName("buttoncancel")
        self.lineeditcartoonname = QtGui.QLineEdit(save)
        self.lineeditcartoonname.setGeometry(QtCore.QRect(108, 22, 313, 24))
        self.lineeditcartoonname.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineeditcartoonname.setObjectName("lineeditcartoonname")
        self.lineeditcaveroute = QtGui.QLineEdit(save)
        self.lineeditcaveroute.setGeometry(QtCore.QRect(108, 54, 313, 24))
        self.lineeditcaveroute.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineeditcaveroute.setObjectName("lineeditcaveroute")
        self.buttonbrowse = QtGui.QPushButton(save)
        self.buttonbrowse.setGeometry(QtCore.QRect(442, 51, 70, 26))
        self.buttonbrowse.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"border:outset\n"
"")
        self.buttonbrowse.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/browse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonbrowse.setIcon(icon2)
        self.buttonbrowse.setIconSize(QtCore.QSize(68, 24))
        self.buttonbrowse.setObjectName("buttonbrowse")
        self.checkBox = QtGui.QCheckBox(save)
        self.checkBox.setGeometry(QtCore.QRect(20, 86, 171, 23))
        self.checkBox.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";")
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(save)
        QtCore.QMetaObject.connectSlotsByName(save)

    def retranslateUi(self, save):
        save.setWindowTitle(QtGui.QApplication.translate("save", "save", None, QtGui.QApplication.UnicodeUTF8))
        self.labelcartoonname.setText(QtGui.QApplication.translate("save", "动 画 名 称 ：", None, QtGui.QApplication.UnicodeUTF8))
        self.labelsaveroute.setText(QtGui.QApplication.translate("save", "保 存 路 径 ：", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("save", "添加到转换任务列表", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
