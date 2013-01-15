#!/usr/bin/python

import sys, os
from datetime import datetime
from PySide import QtCore, QtGui

import SimpleXMLRPCServer
import hashlib

from sqlalchemy import Column, Integer, Sequence, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

import images_rc


engine = create_engine ('mssql://CartoonAdmin:CartoonServerPassword@61.147.79.115/CartoonServer', module = pyodbc)
base = declarative_base()

class User (base):
	__tablename__ = 'T_Users'

	id = Column (Integer, Sequence ('user_id_seq'), primary_key = True)
	Username = Column (String, unique = True)
	Password = Column (String)
	LastLogin = Column (DateTime)

	def __init__ (self, username, password, lastlogin):
		self.Username = username
		self.Password = password
		self.LastLogin = lastlogin

	def __repr__ (self):
		return "<User ('%s', '%s', '%s')>" % (self.Username, self.Password, self.LastLogin)


class ServerTray (QtCore.QObject):

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.quitact = QtGui.QAction (self.tr ("&Quit"), self, triggered = sys.exit)

		self.trayicon = QtGui.QSystemTrayIcon (QtGui.QIcon (':/images/icon.png'))

		self.trayiconmenu = QtGui.QMenu()
		self.trayiconmenu.addAction (self.quitact)

		self.trayicon.setToolTip (self.tr("Minimize to system tray. Right click this icon and choose Quit to close."))
		self.trayicon.setContextMenu (self.trayiconmenu)

		self.trayicon.show()


class RequestHandler (SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
	pass

class CheckLogin (QtCore.QThread):

	def __init__ (self):
		QtCore.QThread.__init__ (self)

		self.server = SimpleXMLRPCServer.SimpleXMLRPCServer (("", 10207), requestHandler = RequestHandler)
		self.server.register_function (self.CheckLogin, 'CheckLogin')

		print "Server successfully running..."

	def run (self):
		self.server.serve_forever()

	def CheckLogin (self, username, password):

		Session = sessionmaker (bind = engine)
		self.session = Session()

		q = self.session.query (User).filter_by (Username = username)
		if not q.count() == 1:
			return False

		pswd = q.first().Password
		if not pswd == password:
			return False

		q.LastLogin = datetime.now()
		self.session.commit()
		return True


if __name__ == "__main__":

	app = QtGui.QApplication (sys.argv)
	QtGui.QApplication.setQuitOnLastWindowClosed (False)

	locale = QtCore.QLocale.system().name()
	appTranslator = QtCore.QTranslator()
	if appTranslator.load ("cartoon_" + locale):
		app.installTranslator (appTranslator)

	tray = ServerTray()

	server = CheckLogin()
	server.start()

	app.exec_()
	server.quit()
	sys.exit()
