#!/usr/bin/python

import time
from datetime import datetime
from PySide import QtCore, QtGui

from sqlalchemy.orm import sessionmaker, scoped_session

import xmlrpclib
import base64

from Models import User, Engine


class RPCHandler (QtCore.QObject):

	startchecklogin = QtCore.Signal (unicode, unicode)
	checkloginsignal = QtCore.Signal (tuple)
	checkloginfinished = QtCore.Signal()
	newmergedfinished = QtCore.Signal()
	newsplittedfinished = QtCore.Signal()
	newtransferredfinished = QtCore.Signal()

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.rpc = xmlrpclib.ServerProxy ("http://61.147.79.115:10207")

	@QtCore.Slot (unicode, unicode)
	def checklogin (self, username, password):
		try:
			islogin, edited, transferred, blastsplittime, blastsplitfile, blastsplitpath, blastmergepath, blasttransferpath = self.rpc.CheckLogin (username, password)
		except:
			self.checkloginsignal.emit ((False, 0, 0, None, None, None, None, None))
			self.checkloginfinished.emit()
			return

		if blastsplittime:
			lastsplittime = base64.b64decode (blastsplittime).decode ('utf-8')
		else:
			lastsplittime = None

		if blastsplitfile:
			lastsplitfile = base64.b64decode (blastsplitfile).decode ('utf-8')
		else:
			lastsplitfile = None

		if blastsplitpath:
			lastsplitpath = base64.b64decode (blastsplitpath).decode ('utf-8')
		else:
			lastsplitpath = None

		if blastmergepath:
			lastmergepath = base64.b64decode (blastmergepath).decode ('utf-8')
		else:
			lastmergepath = None

		if blasttransferpath:
			lasttransferpath = base64.b64decode (blasttransferpath).decode ('utf-8')
		else:
			lasttransferpath = None

		self.checkloginsignal.emit ((islogin, edited, transferred, lastsplittime, lastsplitfile, lastsplitpath, lastmergepath, lasttransferpath))
		self.checkloginfinished.emit()

	@QtCore.Slot (unicode, unicode)
	def newmerged (self, username, path):
		bpath = base64.b64encode (path.encode ('utf-8'))
		while not self.rpc.NewMerged (username, bpath):
			time.sleep (10)

		self.newmergedfinished.emit()

	@QtCore.Slot (unicode, unicode, unicode, unicode)
	def newsplitted (self, username, time, filename, path):
		btime = base64.b64encode (time.encode ('utf-8'))
		bfilename = base64.b64encode (filename.encode ('utf-8'))
		bpath = base64.b64encode (path.encode ('utf-8'))
		while not self.rpc.NewSplitted (username, btime, bfilename, bpath):
			time.sleep (10)

		self.newsplittedfinished.emit()

	@QtCore.Slot (unicode, unicode)
	def newtransferred (self, username, path):
		bpath = base64.b64encode (path.encode ('utf-8'))
		while not self.rpc.NewTransferred (username, bpath):
			time.sleep (10)

		self.newtransferredfinished.emit()


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
			transferred = record.NumTransferred
			lastsplittime = record.LastSplitTime
			lastsplitfile = record.LastSplitFile
			lastsplitpath = record.LastSplitPath
			lastmergepath = record.LastMergePath
			lasttransferpath = record.LastTransferPath

			record.LastLogin = datetime.now()
			return (True, edited, transferred, lastsplittime, lastsplitfile, lastsplitpath,
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

	def NewTransferred (self, username, path):

		session = self.Session()

		with session.begin():

			q = session.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return False

			record = q.first()
			record.NumTransferred += 1
			record.LastTransferPath = path
			return True
