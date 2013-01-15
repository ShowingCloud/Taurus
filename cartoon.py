#!/usr/bin/python

import sys
from PySide import QtCore, QtGui

from Frontend import MainWindow, Login, LoginList
import Translations


if __name__ == "__main__":

	app = QtGui.QApplication (sys.argv)
	app.setWindowIcon (QtGui.QIcon (':/images/icon.ico'))

	scr = QtGui.QApplication.desktop().screenGeometry()

	QtGui.QApplication.setQuitOnLastWindowClosed (False)

	locale = QtCore.QLocale.system().name()
	appTranslator = QtCore.QTranslator()
	if appTranslator.load (":/cartoon_" + locale):
		app.installTranslator (appTranslator)

	islogin = False

	l = Login()
	l.move (scr.center() - l.rect().center())

	while not islogin:

		if not l.exec_() == QtGui.QDialog.Accepted:
			sys.exit()

		ll = LoginList (l.username, l.password)
		ll.move (l.pos())
		ret = ll.exec_()

		if ret == QtGui.QDialog.Rejected:
			sys.exit()
		elif ret == QtGui.QDialog.Accepted:
			islogin = True
		else:
			l.show()
			mbox = QtGui.QMessageBox()
			mbox.setText (QtCore.QObject().tr ("Login error."))
			mbox.exec_()
			islogin = False

	w = MainWindow (l.username, ll.edited, ll.transfered, ll.lastsplittime, ll.lastsplitfile, ll.lastsplitpath, ll.lastmergepath, ll.lasttransferpath)
	w.move (scr.center() - w.rect().center())
	w.show()
	sys.exit (app.exec_())
