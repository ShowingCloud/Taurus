#!/usr/bin/python

import os
from PySide import QtCore, QtGui

from UI import Ui_save


class SaveSplit (QtGui.QDialog):

	def __init__ (self, path, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_save()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

#		self.setWindowTitle (self.tr (""))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.splitpath = path
		if os.path.isdir (path):
			self.ui.lineeditcaveroute.setText (path)

		self.splitfile = None

	@QtCore.Slot()
	def on_buttonbrowse_clicked (self):
		newpath = QtGui.QFileDialog.getExistingDirectory (self, self.tr ("Select output directory"),
				self.ui.lineeditcaveroute.text())
		if not os.path.isdir (newpath):
			newpath = ""

		self.splitpath = newpath
		self.ui.lineeditcaveroute.setText (newpath)

	@QtCore.Slot()
	def on_buttonsave_clicked (self):
		if not os.path.isdir (self.ui.lineeditcaveroute.text()):
			self.on_buttonbrowse_clicked()
		else:
			self.splitpath = self.ui.lineeditcaveroute.text()

		self.splitfile = self.ui.lineeditcartoonname.text()

		if self.splitpath == "" or self.splitfile == "":
			return

		self.accept()

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		self.reject()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 5, 5)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))

	def keyPressEvent (self, event):
		super (SaveSplit, self).keyPressEvent (event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.reject()
			QtGui.qApp.quit()
		elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
			self.accept()

	def mouseMoveEvent (self, event):
		super (SaveSplit, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (SaveSplit, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (SaveSplit, self).mouseReleaseEvent (event)
		self.leftclicked = False
