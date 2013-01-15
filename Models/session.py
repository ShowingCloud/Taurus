#!/usr/bin/python

from sqlalchemy import Column, Integer, Sequence, DateTime

from Models import base


class Session (base):
	__tablename__ = 'T_Sessions'

	id = Column (Integer, Sequence ('session_id_seq'), primary_key = True)
	Session = Column (Integer, unique = True)
	Password = Column (Integer)
	CreateTime = Column (DateTime)
	User = Column (Integer)

	def __init__ (self, session, password, createtime, user):
		self.Session = session
		self.Password = password
		self.CreateTime = createtime
		self.User = user

	def __repr__ (self):
		return "<User ('%d', '%d', '%s', '%d')>" % (self.Session, self.Password,
				self.CreateTime, self.User)
