#!/usr/bin/python

from PySide import QtCore, QtGui


class NewConvertDelegate (QtGui.QStyledItemDelegate):

	deleterow = QtCore.Signal (int)

	def __init__ (self, parent = None):
		QtGui.QStyledItemDelegate.__init__ (self, parent)

	def paint (self, painter, option, index):
		style = QtGui.QApplication.style()

		label = QtGui.QStyleOptionViewItemV4 (option)

		label.font.setFamily ("SimHei")
		label.font.setPointSize (12)

		if index.column() == 1:
			label.displayAlignment = QtCore.Qt.AlignCenter
			label.font.setUnderline (True)
			label.text = self.tr ("Delete")
			label.palette.setColor (QtGui.QPalette.Text, QtGui.QColor (QtCore.Qt.blue))
		else:
			label.displayAlignment = QtCore.Qt.AlignLeft
			label.text = index.data()

		style.drawControl (QtGui.QStyle.CE_ItemViewItem, label, painter)

	def createEditor (self, parent, option, index):
		if index.column() == 1:
			self.deleterow.emit (index.row())
		else:
			pass
