#!/usr/bin/python

from PySide import QtCore, QtGui

from UI import Ui_forgetpassword


class ForgetPassword (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_forgetpassword()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

#		self.setWindowTitle (self.tr ("Forget Password"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

	@QtCore.Slot()
	def on_buttonconfirm_clicked (self):
		self.accept()

	@QtCore.Slot()
	def on_pushButton_clicked (self):
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
		super (ForgetPassword, self).keyPressEvent (event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.reject()
			QtGui.qApp.quit()
		elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
			self.accept()

	def mouseMoveEvent (self, event):
		super (ForgetPassword, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (ForgetPassword, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (ForgetPassword, self).mouseReleaseEvent (event)
		self.leftclicked = False
