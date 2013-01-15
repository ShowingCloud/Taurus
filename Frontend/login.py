#!/usr/bin/python

from PySide import QtCore, QtGui

import time, sys

from UI import Ui_Login
from Frontend import ForgetPassword


class Login (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_Login()
		self.ui.setupUi (self)
		self.ui.lineeditpassword.setEchoMode (QtGui.QLineEdit.Password)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform: Login"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.ui.lineeditcpid.installEventFilter (self)
		self.ui.lineeditpassword.installEventFilter (self)
		self.ui.lineeditcpid.setFocus()

		self.username = None
		self.password = None

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		sys.exit()

	@QtCore.Slot()
	def on_buttonaccept_clicked (self):
		if self.ui.lineeditcpid.text() == "":
			self.twinkle (self.ui.labelcpid, self.ui.lineeditcpid)
			return
		elif self.ui.lineeditpassword.text() == "":
			self.twinkle (self.ui.labelpassword, self.ui.lineeditpassword)
			return

		self.username = self.ui.lineeditcpid.text()
		self.password = self.ui.lineeditpassword.text()

		self.accept()

	@QtCore.Slot()
	def on_buttonforgetpassword_clicked (self):
		msg = ForgetPassword()
		msg.move (self.pos() + self.rect().center() - msg.rect().center())
		msg.exec_()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 7, 14)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))

	def eventFilter (self, obj, event):
		if obj == self.ui.lineeditcpid:
			if event.type() == QtCore.QEvent.KeyPress:
				if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
					if self.ui.lineeditcpid.text() == "":
						self.twinkle (self.ui.labelcpid, self.ui.lineeditcpid)
						return True
					elif self.ui.lineeditpassword.text() == "":
						self.twinkle (self.ui.labelpassword, self.ui.lineeditpassword)
						return True
					else:
						self.ui.buttonaccept.clicked.emit()
				else:
					self.ui.lineeditpassword.clear()
			elif event.type() == QtCore.QEvent.FocusOut:
				if self.ui.lineeditcpid.text() == "":
					self.twinkle (self.ui.labelcpid, self.ui.lineeditcpid)
					return True
#				elif self.ui.lineeditpassword.text() == "":
#					self.twinkle (self.ui.labelpassword, self.ui.lineeditpassword)
#					return False

		elif obj == self.ui.lineeditpassword:
			if event.type() == QtCore.QEvent.KeyPress:
				if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
					if self.ui.lineeditcpid.text() == "":
						self.twinkle (self.ui.labelcpid, self.ui.lineeditcpid)
						return True
					elif self.ui.lineeditpassword.text() == "":
						self.twinkle (self.ui.labelpassword, self.ui.lineeditpassword)
						return True
					else:
						self.ui.buttonaccept.clicked.emit()
						return True
			elif event.type() == QtCore.QEvent.MouseButtonPress:
				if self.ui.lineeditcpid.text() == "":
					self.twinkle (self.ui.labelcpid, self.ui.lineeditcpid)
					return True

		elif event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
			self.ui.buttonaccept.clicked.emit()
			return True

		return QtGui.QWidget.eventFilter (self, obj, event)

	def twinkle (self, label, lineedit):
		labelorig = label.styleSheet()
		lineeditorig = lineedit.styleSheet()
		shining = "background-color: rgb(102, 102, 102); font: 12pt \"SimHei\"; color: rgb(102, 102, 102);"

		for i in xrange (3):
#			label.setStyleSheet (shining)
			lineedit.setStyleSheet (shining)
			self.repaint()
			time.sleep (0.01)
#			label.setStyleSheet (labelorig)
			lineedit.setStyleSheet (lineeditorig)
			self.repaint()
			time.sleep (0.01)

		lineedit.setFocus()

	def keyPressEvent (self, event):
		super (Login, self).keyPressEvent (event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.reject()
			QtGui.qApp.quit()

	def mouseMoveEvent (self, event):
		super (Login, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (Login, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.pos()

	def mouseReleaseEvent (self, event):
		super (Login, self).mouseReleaseEvent (event)
		self.leftclicked = False
