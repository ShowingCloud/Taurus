#!/usr/bin/python

import time
from datetime import datetime, timedelta
import hashlib, random, types, string
import json, base64
import xmlrpclib

from sqlalchemy.orm import sessionmaker, scoped_session
from PySide import QtCore, QtGui

from Models import User, Engine, Session
from config import ALLOW_NOWDG_LOGIN, ALLOW_NOWDG_REG


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
			self._token = hashlib.sha512 (self._token).hexdigest()
			self._longtoken = ''.join ([self._longtoken, self._token])

		try:
			cleartext = ''.join ([chr (ord (a) ^ ord (b)) for a, b in zip (base64.b64decode (params), self._longtoken)]).decode ('utf-8')
			return self.jdec (cleartext)
		except:
			return None

	def _encrypt (self, params):

		params = self.jenc (params)

		while len (params) > len (self._longtoken):
			self._token = hashlib.sha512 (self._token).hexdigest()
			self._longtoken = ''.join ([self._longtoken, self._token])

		cipher = base64.b64encode (''.join ([chr (ord (a) ^ ord (b)) for a, b in zip (params.encode ('utf-8'), self._longtoken)]))
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
			password = record.Password

			if len (password) <= 10:
				self._token = self._username
			else:
				self._token = record.Password
			self._longtoken = ''
			self._user = record.id

		ret = self._decrypt (hello)
		if ret and type (ret) is types.DictType and ret.get ('hello') == hashlib.sha512 (self._hello).hexdigest():
			return ret.get ('newtoken')

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
		if not params.get ('newsession') or not params.get ('newpassword'):
			return False
		self._session = params['newsession']
		self._password = params['newpassword']

		self._token = '#'.join ([str (self._session), str (self._password)])
		self._longtoken = ''
		return True


PreLoginFailed, PreLoginConnFailed, PreLoginOK = xrange (3)

class RPCHandler (QtCore.QObject, SecureSession):

	startchecklogin = QtCore.Signal (unicode, unicode, unicode)
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

		self.rpc = xmlrpclib.ServerProxy ("http://www.zhufengxm.com:10207")

	def PrepareLogin (self, username, password, key):

		ret = PreLoginFailed, None, None

		if key == '4646464646464646' and not ALLOW_NOWDG_LOGIN:
			return ret

		for i in xrange (3):
			try:
				salt = self.rpc.GetSalt (self.jenc (username))
				ret = PreLoginFailed, None, None
			except:
				ret = PreLoginConnFailed, None, None
				continue

			try:
				salt = self.jdec (salt)
				if not salt == None:
					ret = PreLoginOK, None, None
					break
			except:
				continue

		if not ret[0] == PreLoginOK:
			return ret

		if salt == '':
			if key == '4646464646464646' and not ALLOW_NOWDG_REG:
				return PreLoginFailed, None, None

			token = username
		else:
			token = '%s#%s$%s@%s' % (username, password, key, salt)
			token = hashlib.sha512 (token).hexdigest()
			token = '%s%s' % (salt, token)

		newsalt = ''.join (random.choice (string.printable) for i in xrange (10))
		newtoken = '%s#%s$%s@%s' % (username, password, key, newsalt)
		newtoken = hashlib.sha512 (newtoken).hexdigest()
		newtoken = '%s%s' % (newsalt, newtoken)

		return PreLoginOK, token, newtoken

	@QtCore.Slot (unicode, unicode, unicode)
	def checklogin (self, username, password, key):

		self._username = username

		ret, token, newtoken = self.PrepareLogin (username, password, key)
		if ret == PreLoginFailed:
			self.checkloginfinished.emit ((False, dict()))
			return
		elif ret == PreLoginConnFailed:
			self.checkloginfinished.emit ((False, {'except': True}))
			return

		self._token = token
		self._longtoken = ''

		hello = {'hello': hashlib.sha512 (self._hello).hexdigest(),
				'arandom': random.randint (0, 2e9),
				'zrandom': random.randint (0, 2e9),
				'newtoken': newtoken}
		hello = self._encrypt (hello)

		ret = None
		for i in xrange (3):
			try:
				ret = self.rpc.CheckLogin (self.jenc (username), self.jenc (hello))
				resp = (False, dict())
			except:
				resp = (False, {'except': True})
				continue

			try:
				ret = self.jdec (ret)
				if ret:
					resp = True
					break
			except:
				continue

		if not resp == True:
			self.checkloginfinished.emit (resp)
			return

		ret = self._decrypt (ret)
		if ret and type (ret) is types.DictType and ret.get ('ret'):
			if self._readnewsession (ret):
				self.checkloginfinished.emit ((True, ret.get ('Parameters')))

				self.renewtimer = QtCore.QTimer()
				self.renewtimer.timeout.connect (self.renewsession)
				self.renewtimer.start (180000)
				return

		self.checkloginfinished.emit ((False, dict()))

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

	def GetSalt (self, username):

		try:
			username = self.jdec (username)
		except:
			return self.jenc (None)

		sess = self.SQLSession()
		with sess.begin():

			q = sess.query (User).filter_by (Username = username)
			if not q.count() == 1:
				return self.jenc (None)

			record = q.first()
			password = record.Password

			if len (password) <= 10:
				salt = ''
			else:
				salt = password[:10]

			return self.jenc (salt)

	def CheckLogin (self, username, hello):

		try:
			username = self.jdec (username)
			hello = self.jdec (hello)
		except:
			return self.jenc (None)

		self._username = username
		newtoken = self._login_checkin (hello)
		if not newtoken:
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
				params = dict()
				record.Parameters = self.jenc (params)

			params.update ({'NumEdited': edited, 'NumTransferred': transferred})

			record.Password = newtoken
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
