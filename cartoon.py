#!/usr/bin/python

import sys, os
from PySide import QtCore, QtGui

from Frontend import MainWindow, Login, LoginList, PasswordError
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
			QtGui.qApp.quit()

		ll = LoginList (l.username, l.password)
		ll.move (l.pos() + l.rect().center() - ll.rect().center())
		ret = ll.exec_()

		if ret == QtGui.QDialog.Accepted:
			islogin = True
		else:
			l.show()
			l.ui.lineeditcpid.setFocus()

			pe = PasswordError()
			pe.move (l.pos() + l.rect().center() - pe.rect().center())
			pe.exec_()
			islogin = False

	w = MainWindow (ll.rpc, ll.rpcworker, ll.params)
	w.move (scr.center() - w.rect().center())
	w.show()

	sys.exit (app.exec_())
