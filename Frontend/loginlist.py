#!/usr/bin/python

from PySide import QtCore, QtGui

import sys

from UI import Ui_loginlist
from Toolkit import RPCHandler


class LoginList (QtGui.QDialog):

	def __init__ (self, username, password, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_loginlist()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)

		self.rpcworker.startchecklogin.connect (self.rpcworker.checklogin)
		self.rpcworker.checkloginsignal.connect (self.login)
		self.rpcworker.checkloginfinished.connect (self.rpc.quit)
		self.rpcworker.checkloginfinished.connect (self.rpcworker.deleteLater)
		self.rpc.start()
		self.rpcworker.startchecklogin.emit (username, password)

		self.ui.progressBar.setValue (50)

	@QtCore.Slot (list)
	def login (self, ret):
		success, edited, transfered, lastsplittime, lastsplitfile, lastsplitpath, lastmergepath, lasttransferpath = ret
		if success:
			self.ui.progressBar.setValue (100)
			self.edited = edited
			self.transfered = transfered
			self.lastsplittime = lastsplittime
			self.lastsplitfile = lastsplitfile
			self.lastsplitpath = lastsplitpath
			self.lastmergepath = lastmergepath
			self.lasttransferpath = lasttransferpath
			self.accept()
		else:
			self.ui.progressBar.setValue (0)
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
