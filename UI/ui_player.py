# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'player.ui'
#
# Created: Sat Jun 30 22:43:52 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_player(object):
    def setupUi(self, player):
        player.setObjectName("player")
        player.resize(540, 482)
        player.setMinimumSize(QtCore.QSize(540, 482))
        player.setStyleSheet("background-color: rgb(81, 81, 81);")
        self.gridLayout_2 = QtGui.QGridLayout(player)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelblankprogressright = QtGui.QLabel(player)
        self.labelblankprogressright.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.labelblankprogressright.setText("")
        self.labelblankprogressright.setObjectName("labelblankprogressright")
        self.horizontalLayout_2.addWidget(self.labelblankprogressright)
        self.Sliderprogress = QtGui.QSlider(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Sliderprogress.sizePolicy().hasHeightForWidth())
        self.Sliderprogress.setSizePolicy(sizePolicy)
        self.Sliderprogress.setStyleSheet("\n"
"QSlider::groove:horizontal {                                \n"
"     border: 1px solid #999999;   \n"
"                           \n"
"     height:1px;                                     \n"
"   /*  margin:1px ; */                                        \n"
"     left: 10px; right:10px;                               \n"
" }\n"
"QSlider::handle:horizontal {                                \n"
"    /* border:1px solid #5c5c5c;    */                         \n"
"  border-image:url(:/images/round.png);\n"
"    width: 20px; \n"
"    margin:-3px, -3px,-3px,-3px;                                        \n"
"                             \n"
" } \n"
"QSlider::sub-page:horizontal{                               \n"
" background:rgb(102,102,102);\n"
"border-radius:5px; \n"
"  \n"
"}\n"
"QSlider::add-page:horizontal{                               \n"
" background:rgb(255,255,255);\n"
"border-radius:20px; \n"
"\n"
"}\n"
";\n"
"\n"
"background-color: rgb(0, 0, 0);\n"
"")
        self.Sliderprogress.setOrientation(QtCore.Qt.Horizontal)
        self.Sliderprogress.setObjectName("Sliderprogress")
        self.horizontalLayout_2.addWidget(self.Sliderprogress)
        self.labelblankprogressleft = QtGui.QLabel(player)
        self.labelblankprogressleft.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.labelblankprogressleft.setText("")
        self.labelblankprogressleft.setObjectName("labelblankprogressleft")
        self.horizontalLayout_2.addWidget(self.labelblankprogressleft)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelfilmleft = QtGui.QLabel(player)
        self.labelfilmleft.setMaximumSize(QtCore.QSize(30, 16777215))
        self.labelfilmleft.setText("")
        self.labelfilmleft.setPixmap(QtGui.QPixmap(":/images/filmleft.png"))
        self.labelfilmleft.setObjectName("labelfilmleft")
        self.horizontalLayout_3.addWidget(self.labelfilmleft)
        self.frameaudio = QtGui.QFrame(player)
        self.frameaudio.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.frameaudio.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameaudio.setFrameShadow(QtGui.QFrame.Raised)
        self.frameaudio.setObjectName("frameaudio")
        self.horizontalLayout_3.addWidget(self.frameaudio)
        self.labelfilmright = QtGui.QLabel(player)
        self.labelfilmright.setMaximumSize(QtCore.QSize(30, 16777215))
        self.labelfilmright.setText("")
        self.labelfilmright.setPixmap(QtGui.QPixmap(":/images/filmright.png"))
        self.labelfilmright.setObjectName("labelfilmright")
        self.horizontalLayout_3.addWidget(self.labelfilmright)
        self.horizontalLayout_3.setStretch(0, 5)
        self.horizontalLayout_3.setStretch(1, 80)
        self.horizontalLayout_3.setStretch(2, 5)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtGui.QGroupBox(player)
	self.groupBox.setMinimumSize(QtCore.QSize(140, 16777215))
        self.groupBox.setMaximumSize(QtCore.QSize(140, 16777215))
        self.groupBox.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));\n"
"border:outset\n"
"")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.lineeditduration = QtGui.QLineEdit(self.groupBox)
        self.lineeditduration.setGeometry(QtCore.QRect(1, 6, 139, 20))
        self.lineeditduration.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.lineeditduration.setObjectName("lineeditduration")
        self.horizontalLayout.addWidget(self.groupBox)
        self.labelblankbesideduration = QtGui.QLabel(player)
        self.labelblankbesideduration.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.labelblankbesideduration.setText("")
        self.labelblankbesideduration.setObjectName("labelblankbesideduration")
        self.horizontalLayout.addWidget(self.labelblankbesideduration)
        self.buttonplayerstop = QtGui.QPushButton(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonplayerstop.sizePolicy().hasHeightForWidth())
        self.buttonplayerstop.setSizePolicy(sizePolicy)
        self.buttonplayerstop.setMinimumSize(QtCore.QSize(0, 34))
        self.buttonplayerstop.setMaximumSize(QtCore.QSize(49, 16777215))
        self.buttonplayerstop.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));\n"
"border:outset\n"
"")
        self.buttonplayerstop.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplayerstop.setIcon(icon)
        self.buttonplayerstop.setObjectName("buttonplayerstop")
        self.horizontalLayout.addWidget(self.buttonplayerstop)
        self.buttonplayerbackward = QtGui.QPushButton(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonplayerbackward.sizePolicy().hasHeightForWidth())
        self.buttonplayerbackward.setSizePolicy(sizePolicy)
        self.buttonplayerbackward.setMinimumSize(QtCore.QSize(0, 34))
        self.buttonplayerbackward.setMaximumSize(QtCore.QSize(49, 16777215))
        self.buttonplayerbackward.setStyleSheet("border:outset;background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.buttonplayerbackward.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/previous.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplayerbackward.setIcon(icon1)
        self.buttonplayerbackward.setObjectName("buttonplayerbackward")
        self.horizontalLayout.addWidget(self.buttonplayerbackward)
        self.buttonplayerplay = QtGui.QPushButton(player)
        self.buttonplayerplay.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonplayerplay.sizePolicy().hasHeightForWidth())
        self.buttonplayerplay.setSizePolicy(sizePolicy)
        self.buttonplayerplay.setMinimumSize(QtCore.QSize(0, 34))
        self.buttonplayerplay.setMaximumSize(QtCore.QSize(97, 16777215))
        self.buttonplayerplay.setStyleSheet("border:outset;background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.buttonplayerplay.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplayerplay.setIcon(icon2)
        self.buttonplayerplay.setIconSize(QtCore.QSize(36, 36))
        self.buttonplayerplay.setObjectName("buttonplayerplay")
        self.horizontalLayout.addWidget(self.buttonplayerplay)
        self.buttonplayerforward = QtGui.QPushButton(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonplayerforward.sizePolicy().hasHeightForWidth())
        self.buttonplayerforward.setSizePolicy(sizePolicy)
        self.buttonplayerforward.setMinimumSize(QtCore.QSize(0, 34))
        self.buttonplayerforward.setMaximumSize(QtCore.QSize(48, 16777215))
        self.buttonplayerforward.setStyleSheet("border:outset;background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.buttonplayerforward.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonplayerforward.setIcon(icon3)
        self.buttonplayerforward.setObjectName("buttonplayerforward")
        self.horizontalLayout.addWidget(self.buttonplayerforward)
        self.labelblankbesideforward = QtGui.QLabel(player)
        self.labelblankbesideforward.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.labelblankbesideforward.setText("")
        self.labelblankbesideforward.setObjectName("labelblankbesideforward")
        self.horizontalLayout.addWidget(self.labelblankbesideforward)
        self.buttonvolume = QtGui.QPushButton(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonvolume.sizePolicy().hasHeightForWidth())
        self.buttonvolume.setSizePolicy(sizePolicy)
        self.buttonvolume.setMinimumSize(QtCore.QSize(0, 34))
        self.buttonvolume.setMaximumSize(QtCore.QSize(69, 16777215))
        self.buttonvolume.setStyleSheet("border:outset;background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.buttonvolume.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/volume.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonvolume.setIcon(icon4)
        self.buttonvolume.setObjectName("buttonvolume")
        self.horizontalLayout.addWidget(self.buttonvolume)
        self.labelblankbesidevolume = QtGui.QLabel(player)
        self.labelblankbesidevolume.setMaximumSize(QtCore.QSize(8, 16777215))
        self.labelblankbesidevolume.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.labelblankbesidevolume.setText("")
        self.labelblankbesidevolume.setObjectName("labelblankbesidevolume")
        self.horizontalLayout.addWidget(self.labelblankbesidevolume)
        self.slidervolume = QtGui.QSlider(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slidervolume.sizePolicy().hasHeightForWidth())
        self.slidervolume.setSizePolicy(sizePolicy)
        self.slidervolume.setMinimumSize(QtCore.QSize(0, 34))
        self.slidervolume.setStyleSheet("\n"
"QSlider::groove:horizontal {                                \n"
"     border: 1px solid #999999;  \n"
"     border-radius:5px;\n"
"                           \n"
"     height:2px;                                     \n"
" /*    margin:1px ;  */                                       \n"
"    /* left: 1px;       */                        \n"
" }\n"
"QSlider::handle:horizontal {                                \n"
"    /* border:1px solid #5c5c5c;    */                         \n"
"  border-image:url(:/images/transparent.png);\n"
"    width: 2px; \n"
"    margin:-2px, -2px,-2px,-2px;                                        \n"
"                             \n"
" } \n"
"QSlider::sub-page:horizontal{                               \n"
" background:rgb(102,102,102);\n"
"\n"
"  \n"
"}\n"
"QSlider::add-page:horizontal{                               \n"
" background:rgb(27,45,61);\n"
"\n"
"\n"
"}\n"
";\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.slidervolume.setOrientation(QtCore.Qt.Horizontal)
        self.slidervolume.setObjectName("slidervolume")
        self.horizontalLayout.addWidget(self.slidervolume)
        self.labelblankbesideslider = QtGui.QLabel(player)
        self.labelblankbesideslider.setMaximumSize(QtCore.QSize(20, 16777215))
        self.labelblankbesideslider.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97,97,97, 255), stop:0.954802 rgba(52,52, 52, 255));")
        self.labelblankbesideslider.setText("")
        self.labelblankbesideslider.setObjectName("labelblankbesideslider")
        self.horizontalLayout.addWidget(self.labelblankbesideslider)
        self.horizontalLayout.setStretch(0, 14)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 6)
        self.horizontalLayout.setStretch(3, 6)
        self.horizontalLayout.setStretch(4, 12)
        self.horizontalLayout.setStretch(5, 6)
        self.horizontalLayout.setStretch(6, 1)
        self.horizontalLayout.setStretch(7, 6)
        self.horizontalLayout.setStretch(8, 1)
        self.horizontalLayout.setStretch(10, 2)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtGui.QLabel(player)
        self.label_2.setMinimumSize(QtCore.QSize(0, 38))
        self.label_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(player)
        self.label_3.setMinimumSize(QtCore.QSize(0, 38))
        self.label_3.setStyleSheet("background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.label = QtGui.QLabel(player)
        self.label.setMinimumSize(QtCore.QSize(0, 38))
        self.label.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.buttonminimize = QtGui.QPushButton(player)
        self.buttonminimize.setMinimumSize(QtCore.QSize(0, 30))
        self.buttonminimize.setStyleSheet("border:outset")
        self.buttonminimize.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/images/minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonminimize.setIcon(icon5)
        self.buttonminimize.setObjectName("buttonminimize")
        self.horizontalLayout_5.addWidget(self.buttonminimize)
        self.buttonmaximize = QtGui.QPushButton(player)
        self.buttonmaximize.setMinimumSize(QtCore.QSize(0, 30))
        self.buttonmaximize.setStyleSheet("border:outset")
        self.buttonmaximize.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/images/maximize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonmaximize.setIcon(icon6)
        self.buttonmaximize.setObjectName("buttonmaximize")
        self.horizontalLayout_5.addWidget(self.buttonmaximize)
        self.buttonclose = QtGui.QPushButton(player)
        self.buttonclose.setMinimumSize(QtCore.QSize(0, 30))
        self.buttonclose.setStyleSheet("border:outset")
        self.buttonclose.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/images/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonclose.setIcon(icon7)
        self.buttonclose.setObjectName("buttonclose")
        self.horizontalLayout_5.addWidget(self.buttonclose)
        self.labelblankbesideclose = QtGui.QLabel(player)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelblankbesideclose.sizePolicy().hasHeightForWidth())
        self.labelblankbesideclose.setSizePolicy(sizePolicy)
        self.labelblankbesideclose.setMinimumSize(QtCore.QSize(12, 30))
        self.labelblankbesideclose.setText("")
        self.labelblankbesideclose.setObjectName("labelblankbesideclose")
        self.horizontalLayout_5.addWidget(self.labelblankbesideclose)
        self.horizontalLayout_5.setStretch(0, 469)
        self.horizontalLayout_5.setStretch(1, 17)
        self.horizontalLayout_5.setStretch(2, 17)
        self.horizontalLayout_5.setStretch(3, 17)
        self.horizontalLayout_5.setStretch(4, 12)
        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        self.gridLayout.setRowStretch(0, 11)
        self.gridLayout.setRowStretch(1, 102)
        self.gridLayout.setRowStretch(2, 5)
        self.gridLayout.setRowStretch(3, 10)
        self.gridLayout.setRowStretch(4, 30)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(player)
        QtCore.QMetaObject.connectSlotsByName(player)

    def retranslateUi(self, player):
        player.setWindowTitle(QtGui.QApplication.translate("player", "player", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
