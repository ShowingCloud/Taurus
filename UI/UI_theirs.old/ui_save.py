# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'save.ui'
#
# Created: Mon Jul 02 00:03:30 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_save(object):
    def setupUi(self, save):
        save.setObjectName(_fromUtf8("save"))
        save.resize(540, 152)
        save.setMinimumSize(QtCore.QSize(540, 152))
        save.setStyleSheet(_fromUtf8("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(242, 242, 242, 255), stop:1 rgba(153,153, 153, 255));"))
        self.labelcartoonname = QtGui.QLabel(save)
        self.labelcartoonname.setGeometry(QtCore.QRect(14, 26, 101, 16))
        self.labelcartoonname.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";"))
        self.labelcartoonname.setObjectName(_fromUtf8("labelcartoonname"))
        self.labelsaveroute = QtGui.QLabel(save)
        self.labelsaveroute.setGeometry(QtCore.QRect(14, 60, 117, 16))
        self.labelsaveroute.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";"))
        self.labelsaveroute.setObjectName(_fromUtf8("labelsaveroute"))
        self.groupBox = QtGui.QGroupBox(save)
        self.groupBox.setGeometry(QtCore.QRect(0, 118, 543, 34))
        self.groupBox.setStyleSheet(_fromUtf8("background-color: rgb(153, 153, 153);\n"
"border:outset"))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.buttonsave = QtGui.QPushButton(self.groupBox)
        self.buttonsave.setGeometry(QtCore.QRect(394, 4, 70, 26))
        self.buttonsave.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255,0);\n"
"border:outset\n"
"\n"
""))
        self.buttonsave.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/savesave.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonsave.setIcon(icon)
        self.buttonsave.setIconSize(QtCore.QSize(68, 24))
        self.buttonsave.setObjectName(_fromUtf8("buttonsave"))
        self.buttoncancel = QtGui.QPushButton(self.groupBox)
        self.buttoncancel.setGeometry(QtCore.QRect(466, 4, 70, 26))
        self.buttoncancel.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"border:outset"))
        self.buttoncancel.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/savecancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttoncancel.setIcon(icon1)
        self.buttoncancel.setIconSize(QtCore.QSize(66, 22))
        self.buttoncancel.setObjectName(_fromUtf8("buttoncancel"))
        self.lineeditcartoonname = QtGui.QLineEdit(save)
        self.lineeditcartoonname.setGeometry(QtCore.QRect(108, 22, 313, 24))
        self.lineeditcartoonname.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255); \n"
"border-right-color: rgb(255, 255, 255);\n"
"border-bottom-color: rgb(255, 255, 255);\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-top-color: rgb(105, 105, 105);\n"
"border-left-color:rgb(105, 105, 105);"))
        self.lineeditcartoonname.setObjectName(_fromUtf8("lineeditcartoonname"))
        self.lineeditcaveroute = QtGui.QLineEdit(save)
        self.lineeditcaveroute.setGeometry(QtCore.QRect(108, 54, 313, 24))
        self.lineeditcaveroute.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255); \n"
"border-right-color: rgb(255, 255, 255);\n"
"border-bottom-color: rgb(255, 255, 255);\n"
"border-style:groove;\n"
"border-width:2px;\n"
"border-top-color: rgb(105, 105, 105);\n"
"border-left-color:rgb(105, 105, 105);"))
        self.lineeditcaveroute.setObjectName(_fromUtf8("lineeditcaveroute"))
        self.buttonbrowse = QtGui.QPushButton(save)
        self.buttonbrowse.setGeometry(QtCore.QRect(442, 51, 70, 26))
        self.buttonbrowse.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"border:outset\n"
""))
        self.buttonbrowse.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/savebrowse.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonbrowse.setIcon(icon2)
        self.buttonbrowse.setIconSize(QtCore.QSize(68, 24))
        self.buttonbrowse.setObjectName(_fromUtf8("buttonbrowse"))
        self.checkBox = QtGui.QCheckBox(save)
        self.checkBox.setGeometry(QtCore.QRect(20, 86, 171, 23))
        self.checkBox.setStyleSheet(_fromUtf8("background-color: rgba(255, 255, 255, 0);\n"
"font: 10pt \"simhei\";"))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))

        self.retranslateUi(save)
        QtCore.QMetaObject.connectSlotsByName(save)

    def retranslateUi(self, save):
        save.setWindowTitle(QtGui.QApplication.translate("save", "save", None, QtGui.QApplication.UnicodeUTF8))
        self.labelcartoonname.setText(QtGui.QApplication.translate("save", "动 画 名 称 ：", None, QtGui.QApplication.UnicodeUTF8))
        self.labelsaveroute.setText(QtGui.QApplication.translate("save", "保 存 路 径 ：", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("save", "添加到转换任务列表", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
