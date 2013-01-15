#!/usr/bin/python

from PySide import QtCore, QtGui

from UI import Ui_loaderror


class LoadError (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_loaderror()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

#		self.setWindowTitle (self.tr ("Forget Password"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

	@QtCore.Slot()
	def on_buttonload_clicked (self):
		self.ui.buttonload.hide()
		self.ui.labeltxt.setGeometry (QtCore.QRect (0, 10, 400, 120))
		self.ui.labeltxt.setText (self.tr ("Video Source Requirements:\nEncapsulation: MPG, AVI, WMV, VOB\nResolution: Not Lower Than VGA (640 x 480) or D1 (720 x 576)\nBitrate: Not Less Than 4Mbps (for Video) and 128Kbps (for Audio)\nFramerate: Not Less Than 25 Frames/second"))

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		self.accept()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 7, 14)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))

	def keyPressEvent (self, event):
		super (LoadError, self).keyPressEvent (event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.reject()
			QtGui.qApp.quit()
		elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
			self.accept()

	def mouseMoveEvent (self, event):
		super (LoadError, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (LoadError, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (LoadError, self).mouseReleaseEvent (event)
		self.leftclicked = False
