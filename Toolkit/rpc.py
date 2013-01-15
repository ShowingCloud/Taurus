#!/usr/bin/python

from PySide import QtCore, QtGui

import xmlrpclib

class RPCHandler (QtCore.QObject):

	startchecklogin = QtCore.Signal (unicode, unicode)
	checkloginsignal = QtCore.Signal (list)
	checkloginfinished = QtCore.Signal()

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.rpc = xmlrpclib.ServerProxy ("http://61.147.79.115:10207")

	@QtCore.Slot (unicode, unicode)
	def checklogin (self, username, password):
		self.checkloginsignal.emit (self.rpc.CheckLogin (username, password))
#		self.checkloginsignal.emit ([True, 0, 0])
		self.checkloginfinished.emit()
