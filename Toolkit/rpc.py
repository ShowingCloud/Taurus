#!/usr/bin/python

import time
from PySide import QtCore, QtGui

import xmlrpclib

class RPCHandler (QtCore.QObject):

	startchecklogin = QtCore.Signal (unicode, unicode)
	checkloginsignal = QtCore.Signal (list)
	checkloginfinished = QtCore.Signal()
	startnewmerged = QtCore.Signal (unicode, unicode)
	newmergedfinished = QtCore.Signal()
	startnewsplitted = QtCore.Signal (unicode, unicode, unicode, unicode)
	newsplittedfinished = QtCore.Signal()
	startnewtransferred = QtCore.Signal (unicode, unicode)
	newtransferredfinished = QtCore.Signal()

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.rpc = xmlrpclib.ServerProxy ("http://61.147.79.115:10207")

	@QtCore.Slot (unicode, unicode)
	def checklogin (self, username, password):
		self.checkloginsignal.emit (self.rpc.CheckLogin (username, password))
		self.checkloginfinished.emit()

	@QtCore.Slot (unicode, unicode)
	def newmerged (self, username, path):
		while not self.rpc.NewMerged (username, path):
			time.sleep (10)

		self.newmergedfinished.emit()

	@QtCore.Slot (unicode, unicode, unicode, unicode)
	def newsplitted (self, username, time, filename, path):
		while not self.rpc.NewSplitted (username, time, filename, path):
			time.sleep (10)

		self.newsplittedfinished.emit()

	@QtCore.Slot (unicode, unicode)
	def newtransferred (self, username, path):
		while not self.rpc.NewTransferred (username, path):
			time.sleep (10)

		self.newtransferredfinished.emit()
