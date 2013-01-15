#!/usr/bin/python

import os, time
from PySide import QtCore, QtGui
from ctypes import pythonapi, c_void_p, py_object

from UI import Ui_player
from Backend import Player


class MergeExam (QtGui.QDialog):

	def __init__ (self, filename, path, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.examfile = os.path.join (path, filename)
		if path == "" or filename == "" or not os.path.exists (path) or not os.path.isdir (path) or not os.path.isfile (self.examfile):
			msg = QtGui.QMessageBox()
			msg.setInformativeText (self.tr ("File invalid."))
			msg.exec_()
			print "rejected"
			QtGui.qApp.postEvent (self, QtGui.QCloseEvent())
			return

		self.ui = Ui_player()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		winid = self.ui.frameaudio.winId()
		pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
		pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]
		self.windowId = pythonapi.PyCObject_AsVoidPtr (winid)

		self.playerworker = Player (self.windowId, self.ui.Sliderprogress.minimum(), self.ui.Sliderprogress.maximum(), self.ui.slidervolume.minimum(), self.ui.slidervolume.maximum())
		self.player = QtCore.QThread()
		self.playerworker.moveToThread (self.player)

		self.ui.buttonplayerplay.clicked.connect (self.playerworker.playclicked)
		self.ui.buttonplayerstop.clicked.connect (self.playerworker.stopclicked)
		self.ui.buttonplayerbackward.clicked.connect (self.playerworker.backwardclicked)
		self.ui.buttonplayerforward.clicked.connect (self.playerworker.forwardclicked)
		self.ui.buttonvolume.clicked.connect (self.playerworker.muteornot)
		self.ui.Sliderprogress.valueChanged.connect (self.playerworker.sliderseekvalue)
		self.ui.slidervolume.valueChanged.connect (self.playerworker.slidervolumevalue)

		self.playerworker.playurisignal.connect (self.playerworker.playuri)
		self.playerworker.updatelabelduration.connect (self.updatelabelduration)
		self.playerworker.updatesliderseek.connect (self.updatesliderseek)
		self.playerworker.updateslidervolume.connect (self.updateslidervolume)
		self.playerworker.setbuttonplay.connect (self.playersetbuttonplay)
		self.playerworker.setbuttonpause.connect (self.playersetbuttonpause)

		self.player.started.connect (self.playerworker.startworker)
		self.playerworker.finished.connect (self.player.quit)
		self.playerworker.finished.connect (self.playerworker.deleteLater)
		self.player.finished.connect (self.player.deleteLater)

		QtGui.qApp.aboutToQuit.connect (self.player.quit)
		QtGui.qApp.aboutToQuit.connect (self.player.wait)

		self.player.start()

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect (self.delayedplayuri)
		self.timer.setSingleShot (True)
		self.timer.start (1000)

		self.ui.label_3.setText (QtCore.QFileInfo (self.examfile).fileName())
		self.ui.label_3.setAlignment (QtCore.Qt.AlignHCenter)

		self.ui.lineeditduration.setEnabled (False)

	@QtCore.Slot()
	def delayedplayuri (self):
		print "timer"
		self.playerworker.playurisignal.emit (self.examfile)

	@QtCore.Slot (unicode)
	def updatelabelduration (self, text):
		self.ui.lineeditduration.setText (text)

	@QtCore.Slot (int)
	def updatesliderseek (self, value):
		self.ui.Sliderprogress.blockSignals (True)
		self.ui.Sliderprogress.setValue (value)
		self.ui.Sliderprogress.blockSignals (False)

	@QtCore.Slot (int)
	def updateslidervolume (self, value):
		self.ui.slidervolume.blockSignals (True)
		self.ui.slidervolume.setValue (value)
		self.ui.slidervolume.blockSignals (False)

		self.on_slidervolume_valueChanged (value)

	@QtCore.Slot (int)
	def on_slidervolume_valueChanged (self, value):

		volmax = self.ui.slidervolume.maximum()
		volmin = self.ui.slidervolume.minimum()

		if value == 0:
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/mute.png'))
		elif value < (volmin + (volmax - volmin) / 3):
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/volume.png'))
		elif value < (volmin + (volmax - volmin) * 2 / 3):
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/weakvolume.png'))
		else:
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/strongvolume.png'))

	@QtCore.Slot()
	def playersetbuttonplay (self):
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))

	@QtCore.Slot()
	def playersetbuttonpause (self):
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/pause2.png'))

	def mouseMoveEvent (self, event):
		super (MergeExam, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (MergeExam, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.globalPos() - self.pos()
			self.clickedpos = event.globalPos()

	def mouseReleaseEvent (self, event):
		super (MergeExam, self).mouseReleaseEvent (event)
		self.leftclicked = False

	def mouseDoubleClickEvent (self, event):
		super (MergeExam, self).mouseDoubleClickEvent (event)
		self.on_buttonmaximize_clicked()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 3, 3)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))
