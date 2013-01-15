#!/usr/bin/python

import os
from PySide import QtCore, QtGui

from UI import Ui_newconvert
from Toolkit import NewConvertDelegate


class NewConvert (QtGui.QDialog):

	def __init__ (self, lasttransferpath, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_newconvert()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

#		self.setWindowTitle (self.tr (""))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.transferpath = lasttransferpath
		if os.path.isdir (lasttransferpath):
			self.ui.lineeditoutputroute.setText (lasttransferpath)

		self.files = []

		self.ui.treeView.setModel (self.newconvertmodel (self))
		self.ui.treeView.setRootIsDecorated (False)
		self.ui.treeView.setAlternatingRowColors (True)
		self.ui.treeView.setItemDelegate (NewConvertDelegate (self))
		self.ui.treeView.itemDelegate().deleterow.connect (self.deleterow)
#		self.ui.treeView.setEditTriggers (QtGui.QAbstractItemView.SelectedClicked)
		self.ui.treeView.header().setDefaultAlignment (QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.ui.treeView.header().setDefaultSectionSize (320)
		self.ui.treeView.header().setStretchLastSection (True)
		self.ui.treeView.header().hide()

	@QtCore.Slot (int)
	def deleterow (self, row):
		self.ui.treeView.model().takeRow (row)

	@QtCore.Slot()
	def on_buttonbrowse_clicked (self):
		newpath = QtGui.QFileDialog.getExistingDirectory (self, self.tr ("Select output directory"),
				self.ui.lineeditoutputroute.text())
		if not os.path.isdir (newpath):
			newpath = ""

		self.transferpath = newpath
		self.ui.lineeditoutputroute.setText (newpath)

	@QtCore.Slot()
	def on_buttonplus_clicked (self):
		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"),
				QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MoviesLocation))[0]
		model = self.ui.treeView.model()

		for f in files:
			newfile = QtCore.QFileInfo (f)
			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), newfile.absoluteFilePath())

	def newconvertmodel (self, parent):
		model = QtGui.QStandardItemModel (0, 2, parent)
		return model

	@QtCore.Slot()
	def on_buttonconvert_clicked (self):
		model = self.ui.treeView.model()

		if not os.path.isdir (self.ui.lineeditoutputroute.text()):
			self.on_buttonbrowse_clicked()
		else:
			self.transferpath = self.ui.lineeditoutputroute.text()

		if self.transferpath == "":
			return

		self.files = []

		for i in xrange (model.rowCount()):
			f = model.data (model.index (i, 0))
			if os.path.isfile (f):
				self.files.append (model.data (model.index (i, 0)))

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
		super (NewConvert, self).keyPressEvent (event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.reject()
			QtGui.qApp.quit()
		elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
			self.accept()

	def mouseMoveEvent (self, event):
		super (NewConvert, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (NewConvert, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (NewConvert, self).mouseReleaseEvent (event)
		self.leftclicked = False
