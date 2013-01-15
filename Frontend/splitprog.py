#!/usr/bin/python

from PySide import QtCore, QtGui

import sys

from UI import Ui_loginlist


class SplitProg (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_loginlist()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)
		self.setWindowTitle (self.tr ("Splitter Progress"))

		self.ui.labelcartoonupload.setText (self.tr ("Splitter Progress"))
		self.ui.label.setText (self.tr ("Splitting Video..."))

		self.progress = 0
		self.ui.progressBar.setValue (self.progress)

	@QtCore.Slot (int)
	def setprogressbar (self, value):
		if value > self.ui.progressBar.value():
			self.ui.progressBar.setValue (value)

	@QtCore.Slot()
	def on_pushButton_clicked (self):
		self.hide()

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
		super (SplitProg, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (SplitProg, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (SplitProg, self).mouseReleaseEvent (event)
		self.leftclicked = False
