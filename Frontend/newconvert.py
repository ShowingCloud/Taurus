#!/usr/bin/python

import os
from PySide import QtCore, QtGui

from UI import Ui_newconvert
from Toolkit import NewConvertDelegate
from Frontend import CommonError


class NewConvert (QtGui.QDialog):

	def __init__ (self, lasttransferpath, lasttransfersrcpath, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_newconvert()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		self.setWindowTitle (self.tr ("New Transcode Task"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.transferpath = lasttransferpath
		if lasttransferpath and os.path.isdir (lasttransferpath):
			self.ui.lineeditoutputroute.setText (lasttransferpath)

		self.transfersrcpath = QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MoviesLocation)
		if lasttransfersrcpath and os.path.isdir (lasttransfersrcpath):
			self.transfersrcpath = lasttransfersrcpath

		self.files = list()

		self.ui.treeView.setModel (self.newconvertmodel (self))
		self.ui.treeView.setRootIsDecorated (False)
		self.ui.treeView.setAlternatingRowColors (True)
		self.ui.treeView.setItemDelegate (NewConvertDelegate (self))
		self.ui.treeView.itemDelegate().deleterow.connect (self.deleterow)
		self.ui.treeView.setEditTriggers (QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)
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
			return

		self.transferpath = newpath
		self.ui.lineeditoutputroute.setText (newpath)

	@QtCore.Slot()
	def on_buttonplus_clicked (self):
		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), self.transfersrcpath)[0]
		model = self.ui.treeView.model()

		for f in files:
			newfile = QtCore.QFileInfo (f)
			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()))

	def newconvertmodel (self, parent):
		model = QtGui.QStandardItemModel (0, 2, parent)
		return model

	@QtCore.Slot()
	def on_buttonconvert_clicked (self):
		model = self.ui.treeView.model()

		if os.path.isdir (self.ui.lineeditoutputroute.text()):
			self.transferpath = self.ui.lineeditoutputroute.text()
		else:
			self.on_buttonbrowse_clicked()

		if self.transferpath == "":
			msg = CommonError (self.tr ("Please input output path"))
			msg.exec_()
			return

		self.files = []

		for i in xrange (model.rowCount()):
			f = model.data (model.index (i, 0))
			if os.path.isfile (f):
				self.files.append (f)

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
			self.buttonconvert.clicked.emit()

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
