#!/usr/bin/python

from PySide import QtCore, QtGui

import sys

from UI import Ui_loginlist
from Toolkit import RPCHandler


class LoginList (QtGui.QDialog):

	def __init__ (self, username, password, key, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_loginlist()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)

		self.rpcworker.checkloginfinished.connect (self.login)
		QtGui.qApp.aboutToQuit.connect (self.rpcworker.deleteLater)
		QtGui.qApp.aboutToQuit.connect (self.rpc.quit)
		self.rpc.start()
		self.rpcworker.startchecklogin.emit (username, password, key)

		self.progress = 0
		self.ui.progressBar.setValue (self.progress)
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect (self.setprogressbar)
		self.timer.start (100)

		self.params = None

	@QtCore.Slot()
	def setprogressbar (self):
		self.progress += 1
		self.ui.progressBar.setValue (self.progress)

		if self.progress > 200:
			self.ui.progressBar.setValue (0)
			self.done (2)

	@QtCore.Slot (tuple)
	def login (self, ret):
		success, params = ret
		if success:
			self.ui.progressBar.setValue (100)
			self.params = params
			self.accept()
		else:
			self.ui.progressBar.setValue (0)
			if params.get ('except'):
				self.done (2)
			else:
				self.reject()

	@QtCore.Slot()
	def on_pushButton_clicked (self):
		sys.exit()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 7, 14)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))

	def mouseMoveEvent (self, event):
		super (LoginList, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (LoginList, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (LoginList, self).mouseReleaseEvent (event)
		self.leftclicked = False
