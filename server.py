#!/usr/bin/python

import sys, os, time
from datetime import datetime
from PySide import QtCore, QtGui

import SimpleXMLRPCServer
import hashlib

from sqlalchemy import Column, Integer, Sequence, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

from UI import images_rc
import Translations


Engine = create_engine ('mssql://CartoonAdmin:CartoonServerPassword@61.147.79.115/CartoonServer', module = pyodbc)
base = declarative_base()

class User (base):
	__tablename__ = 'T_Users'

	id = Column (Integer, Sequence ('user_id_seq'), primary_key = True)
	Username = Column (String, unique = True)
	Password = Column (String)
	LastLogin = Column (DateTime)
	NumEdited = Column (Integer)
	NumTransfered = Column (Integer)
	LastSplitTime = Column (String)
	LastSplitFile = Column (String)
	LastSplitPath = Column (String)
	LastMergePath = Column (String)
	LastTransferPath = Column (String)

	def __init__ (self, username, password, lastlogin, numedited, numtransfered, lastsplittime, lastsplitfile,
			lastsplitpath, lastmergepath, lasttransferpath):
		self.Username = username
		self.Password = password
		self.LastLogin = lastlogin
		self.NumEdited = numedited
		self.NumTransfered = numtransfered
		self.LastSplitTime = lastsplittime
		self.LastSplitFile = lastsplitfile
		self.LastSplitPath = lastsplitpath
		self.LastMergePath = lastmergepath
		self.LastTransferPath = lasttransferpath

	def __repr__ (self):
		return "<User ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.Username, self.Password,
				self.LastLogin, self.NumEdited, self.NumTransfered, self.LastSplitTime, self.LastSplitFile,
				self.LastMergePath, self.LastTransferPath)


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


class RPCServerHandler (QtCore.QObject):

	finished = QtCore.Signal()

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.server = SimpleXMLRPCServer.SimpleXMLRPCServer (("", 10207),
				requestHandler = SimpleXMLRPCServer.SimpleXMLRPCRequestHandler, allow_none = True)
		self.server.register_introspection_functions()
		self.server.register_instance (CartoonServer())

		self.server.allow_reuse_address = True

		QtGui.qApp.aboutToQuit.connect (self.quitworker)

	@QtCore.Slot()
	def startworker (self):
		print "Server successfully running..."
		self.server.serve_forever()

		self.finished.emit()
		print "Server exiting..."

	@QtCore.Slot()
	def quitworker (self):
		print "quit worker"
		self.server.shutdown()


class CartoonServer (object):

	def __init__ (self, parent = None):
		self.Session = scoped_session (sessionmaker (bind = Engine, autocommit = True))

	def CheckLogin (self, username, password):

		session = self.Session()

		with session.begin():

			q = session.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return (False, None, None, None, None, None, None, None)

			record = q.first()
			pswd = record.Password
			if not pswd == password:
				return (False, None, None, None, None, None, None, None)

			edited = record.NumEdited
			transfered = record.NumTransfered
			lastsplittime = record.LastSplitTime
			lastsplitfile = record.LastSplitFile
			lastsplitpath = record.LastSplitPath
			lastmergepath = record.LastMergePath
			lasttransferpath = record.LastTransferPath

			record.LastLogin = datetime.now()
			return (True, edited, transfered, lastsplittime, lastsplitfile, lastsplitpath,
					lastmergepath, lasttransferpath)

	def NewMerged (self, username, path):

		session = self.Session()

		with session.begin():

			q = session.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return False

			record = q.first()
			record.NumEdited += 1
			record.LastMergePath = path
			return True

	def NewSplitted (self, username, time, filename, path):

		session = self.Session()

		with session.begin():

			q = session.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return False

			record = q.first()
			record.NumEdited += 1
			record.LastSplitTime = time
			record.LastSplitFile = filename
			record.LastSplitPath = path
			return True

	def NewTransfered (self, username, path):

		session = self.Session()

		with session.begin():

			q = session.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return False

			record = q.first()
			record.NumTransfered += 1
			record.LastTransferPath = path
			return True


if __name__ == "__main__":

	app = QtGui.QApplication (sys.argv)
	app.setWindowIcon (QtGui.QIcon (':/images/icon.ico'))
	QtGui.QApplication.setQuitOnLastWindowClosed (False)

	locale = QtCore.QLocale.system().name()
	appTranslator = QtCore.QTranslator()
	if appTranslator.load (":/cartoon_" + locale):
		app.installTranslator (appTranslator)

	tray = ServerTray()

	serverworker = RPCServerHandler()
	server = QtCore.QThread()
	serverworker.moveToThread (server)

	server.started.connect (serverworker.startworker)
	serverworker.finished.connect (server.quit)
	serverworker.finished.connect (serverworker.deleteLater)
	server.finished.connect (server.deleteLater)

	QtGui.qApp.aboutToQuit.connect (server.quit)
	QtGui.qApp.aboutToQuit.connect (server.wait)

	server.start()

	app.exec_()
	sys.exit()
