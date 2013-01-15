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
	Parameters = Column (String)

	def __init__ (self, username, password, lastlogin, numedited, numtransferred, params):
		self.Username = username
		self.Password = password
		self.LastLogin = lastlogin
		self.NumEdited = numedited
		self.NumTransferred = numtransferred
		self.Parameters = params

	def __repr__ (self):
		return "<User ('%s', '%s', '%s', '%d', '%d', '%s')>" % (self.Username, self.Password,
				self.LastLogin, self.NumEdited, self.NumTransferred, self.Parameters)
