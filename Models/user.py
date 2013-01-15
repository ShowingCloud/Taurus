#!/usr/bin/python

from sqlalchemy import Column, Integer, Sequence, String, DateTime

from Models import base


class User (base):
	__tablename__ = 'T_Users'

	id = Column (Integer, Sequence ('user_id_seq'), primary_key = True)
	Username = Column (String, unique = True)
	Password = Column (String)
	LastLogin = Column (DateTime)
	NumEdited = Column (Integer)
	NumTransferred = Column (Integer)
	LastSplitTime = Column (String)
	LastSplitFile = Column (String)
	LastSplitPath = Column (String)
	LastMergePath = Column (String)
	LastTransferPath = Column (String)

	def __init__ (self, username, password, lastlogin, numedited, numtransferred, lastsplittime, lastsplitfile,
			lastsplitpath, lastmergepath, lasttransferpath):
		self.Username = username
		self.Password = password
		self.LastLogin = lastlogin
		self.NumEdited = numedited
		self.NumTransferred = numtransferred
		self.LastSplitTime = lastsplittime
		self.LastSplitFile = lastsplitfile
		self.LastSplitPath = lastsplitpath
		self.LastMergePath = lastmergepath
		self.LastTransferPath = lasttransferpath

	def __repr__ (self):
		return "<User ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.Username, self.Password,
				self.LastLogin, self.NumEdited, self.NumTransferred, self.LastSplitTime, self.LastSplitFile,
				self.LastMergePath, self.LastTransferPath)
