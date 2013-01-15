#!/usr/bin/python

import time
from datetime import datetime, timedelta
import hashlib, random, types
import json
import xmlrpclib

from sqlalchemy.orm import sessionmaker, scoped_session
from PySide import QtCore, QtGui

from Models import User, Engine, Session


class SecureSession (object):

	def __init__ (self, parent = None):
		self._session = ''
		self._username = ''
		self._password = ''
		self._token = ''
		self._longtoken = ''
		self._user = 0
		self._createtime = datetime.now() - timedelta (minutes = 10)

		self._hello = 'Yeah, this is the right hello message'

		self.jenc = json.JSONEncoder (separators = (',', ':'), sort_keys = True).encode
		self.jdec = json.JSONDecoder().decode

	def _decrypt (self, params):

		while len (params) > len (self._longtoken):
			self._token = hashlib.md5 (self._token).hexdigest()
			self._longtoken = ''.join ([self._longtoken, self._token])

		cleartext = ''.join ([chr (a ^ ord (b)) for a, b in zip (params, self._longtoken)])

		try:
			return self.jdec (cleartext)
		except:
			return None

	def _encrypt (self, params):

		params = self.jenc (params)

		while len (params) > len (self._longtoken):
			self._token = hashlib.md5 (self._token).hexdigest()
			self._longtoken = ''.join ([self._longtoken, self._token])

		cipher = [ord (a) ^ ord (b) for a, b in zip (params, self._longtoken)]
		return cipher

	def _checkin (self, params):

		sess = self.SQLSession()
		with sess.begin():

			q = sess.query (Session).filter_by (Session = self._session)
			if not q.count() == 1:
				return None

			record = q.first()
			self._password = record.Password
			self._user = record.User
			self._createtime = record.CreateTime
			self._token = '#'.join ([str (self._session), str (self._password)])
			self._longtoken = ''

		return self._decrypt (params)

	def _checkout (self, params):
		if datetime.now() - self._createtime > timedelta (minutes = 3):
			params = self._newsession (params)

		return self._encrypt (params)

	def _login_checkin (self, hello):

		sess = self.SQLSession()
		with sess.begin():

			q = sess.query (User).filter_by (Username = self._username)
			if not q.count() == 1:
				return None

			record = q.first()
			self._token = record.Password
			self._longtoken = ''
			self._user = record.id

		ret = self._decrypt (hello)
		if ret and type (ret) is types.DictType and ret.get ('hello') == hashlib.md5 (self._hello).hexdigest():
			return True

		return None

	def _login_checkout (self, params):
		return self._encrypt (self._newsession (params))

	def _newsession (self, params):

		sess = self.SQLSession()
		with sess.begin():

			while True:
				newsession = random.randint (0, 2e9)

				q = sess.query (Session).filter_by (Session = newsession)
				if q.count() == 0:
					break

			newpassword = random.randint (0, 2e9)

			record = Session (session = newsession, password = newpassword,
					createtime = datetime.now(), user = self._user)
			sess.add (record)

		params.update ({'newsession': newsession, 'newpassword': newpassword})
		return params

	def _readnewsession (self, params):
		if not params.has_key ('newsession') or not params.has_key ('newpassword'):
			return False
		self._session = params['newsession']
		self._password = params['newpassword']

		self._token = '#'.join ([str (self._session), str (self._password)])
		self._longtoken = ''
		return True


class RPCHandler (QtCore.QObject, SecureSession):

	startchecklogin = QtCore.Signal (unicode, unicode)
	checkloginfinished = QtCore.Signal (tuple)
	newmergedsignal = QtCore.Signal (dict)
	newsplittedsignal = QtCore.Signal (dict)
	newtransferredsignal = QtCore.Signal (dict)
	renewparamssignal = QtCore.Signal (dict)
	lostconnection = QtCore.Signal()

	def __init__ (self, parent = None):
		QtCore.QObject.__init__ (self, parent)
		SecureSession.__init__ (self, parent)

		self.startchecklogin.connect (self.checklogin)
		self.newmergedsignal.connect (self.newmerged)
		self.newsplittedsignal.connect (self.newsplitted)
		self.newtransferredsignal.connect (self.newtransferred)
		self.renewparamssignal.connect (self.renewparams)

		self.rpc = xmlrpclib.ServerProxy ("http://61.147.79.115:10207")

	@QtCore.Slot (unicode, unicode)
	def checklogin (self, username, password):

		self._username = username
		token = '#'.join ([username, password])
		self._token = hashlib.md5 (token).hexdigest()
		self._longtoken = ''

		hello = {'hello': hashlib.md5 (self._hello).hexdigest(),
				'arandom': random.randint (0, 2e9)}
		hello = self._encrypt (hello)

		try:
			ret = self.rpc.CheckLogin (self.jenc (username), self.jenc (hello))
			ret = self.jdec (ret)
		except:
			self.checkloginfinished.emit ((False, {}))
			return

		if not ret:
			self.checkloginfinished.emit ((False, {}))
			return

		ret = self._decrypt (ret)
		if ret and type (ret) is types.DictType and ret.get ('ret'):
			if self._readnewsession (ret):
				self.checkloginfinished.emit ((True, ret['Parameters']))

				self.renewtimer = QtCore.QTimer()
				self.renewtimer.timeout.connect (self.renewsession)
				self.renewtimer.start (180000)
				return

		self.checkloginfinished.emit ((False, {}))

	def renewsession (self):
		while True:
			try:
				ret = self.rpc.RenewSession (self.jenc (self._session))
				ret = self.jdec (ret)
			except:
				time.sleep (10)
				continue

			if not ret:
				self.lostconnection.emit()
				time.sleep (10)
				continue

			ret = self._decrypt (ret)
			if ret and type (ret) is types.DictType and ret.get ('ret'):
				self._readnewsession (ret)
				break

			self.lostconnection.emit()
			time.sleep (10)
			continue

	def _sendparams (self, params, func):
		params = self._encrypt (params)

		while True:
			try:
				ret = func (self.jenc (self._session), self.jenc (params))
				ret = self.jdec (ret)
			except:
				time.sleep (10)
				continue

			if not ret:
				self.lostconnection.emit()
				time.sleep (10)
				continue

			ret = self._decrypt (ret)
			if ret and type (ret) is types.DictType and ret.get ('ret'):
				self._readnewsession (ret)
				break

			self.lostconnection.emit()
			time.sleep (10)
			continue

	@QtCore.Slot (dict)
	def newmerged (self, params):
		self._sendparams (params, self.rpc.NewMerged)

	@QtCore.Slot (dict)
	def newsplitted (self, params):
		self._sendparams (params, self.rpc.NewSplitted)

	@QtCore.Slot (dict)
	def newtransferred (self, params):
		self._sendparams (params, self.rpc.NewTransferred)

	@QtCore.Slot (dict)
	def renewparams (self, params):
		self._sendparams (params, self.rpc.RenewParams)


MethodCheckLogin, MethodNewMerged, MethodNewSplitted, MethodNewTransferred, MethodRenewParams = xrange (5)

class CartoonServer (SecureSession):

	def __init__ (self, parent = None):
		SecureSession.__init__ (self, parent)

		self.SQLSession = scoped_session (sessionmaker (bind = Engine, autocommit = True))

		self.flushtimer = QtCore.QTimer (QtGui.QApplication.instance())
		self.flushtimer.timeout.connect (self.FlushSession)
		self.flushtimer.start (300000)

	def CheckLogin (self, username, hello):

		try:
			username = self.jdec (username)
			hello = self.jdec (hello)
		except:
			return self.jenc (None)

		self._username = username
		if not self._login_checkin (hello):
			return self.jenc (None)

		sess = self.SQLSession()
		with sess.begin():

			q = sess.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return self.jenc (None)

			record = q.first()

			edited = record.NumEdited
			transferred = record.NumTransferred

			try:
				params = self.jdec (record.Parameters)
			except:
				params = {}
				record.Parameters = self.jenc (params)

			params.update ({'NumEdited': edited, 'NumTransferred': transferred})

			record.LastLogin = datetime.now()

		return self.jenc (self._login_checkout ({'ret': True, 'Parameters': params}))

	def FlushSession (self):
		sess = self.SQLSession()
		with sess.begin():
			deadline = datetime.now() - timedelta (minutes = 10)
			sess.query (Session).filter (Session.CreateTime < deadline).delete()

	def _recvnewparams (self, session, params, method):

		try:
			session = self.jdec (session)
			params = self.jdec (params)
		except:
			return self.jenc (None)

		self._session = session
		params = self._checkin (params)
		if not params or type (params) is not types.DictType:
			return self.jenc (None)

		sess = self.SQLSession()
		with sess.begin():

			q = sess.query (User).filter_by (id = self._user)
			if not q.count() == 1:
				return self.jenc (None)

			record = q.first()

			if method == MethodNewMerged or method == MethodNewSplitted:
				record.NumEdited += 1
			elif method == MethodNewTransferred:
				record.NumTransferred += 1

			if params.has_key ('NumEdited'):
				params.pop ('NumEdited')
			if params.has_key ('NumTransferred'):
				params.pop ('NumTransferred')
			record.Parameters = self.jenc (params)

		return self.jenc (self._checkout ({'ret': True}))

	def NewMerged (self, session, params):
		return self._recvnewparams (session, params, MethodNewMerged)

	def NewSplitted (self, session, params):
		return self._recvnewparams (session, params, MethodNewSplitted)

	def NewTransferred (self, session, params):
		return self._recvnewparams (session, params, MethodNewTransferred)

	def RenewParams (self, session, params):
		return self._recvnewparams (session, params, MethodRenewParams)

	def RenewSession (self, session):
		try:
			session = self.jdec (session)
		except:
			return self.jenc (None)

		self._session = session
		self._checkin ('')

		return self.jenc (self._checkout ({'ret': True}))
