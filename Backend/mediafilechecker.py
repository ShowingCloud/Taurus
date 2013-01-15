#!/usr/bin/python

import os
import gst
from PySide import QtCore

from Toolkit import MediaTypes, Discoverer


class MediaFileChecker (QtCore.QObject):

	discoveredsignal = QtCore.Signal (int, bool, dict)
	finished = QtCore.Signal()

	def __init__ (self, mediafile, row, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.mediafile = mediafile
		self.row = row

		self.params = dict()

		self.finished.connect (self.deleteLater)

	@QtCore.Slot()
	def startworker (self):

		if not os.path.isfile (self.mediafile):
			self.on_discovered (dict(), False)
			return

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.on_timeout)
		self.timeoutcounter = 0
		self.contexttimer.start (100)

		self.discover = Discoverer (self.mediafile)
		self.discover.discover()

	def on_timeout (self):
		self.timeoutcounter += 1

		if self.timeoutcounter > 30 or self.discover.finished:

			if not self.discover._success:
				self.discoveredsignal.emit (self.row, self.discover._success, self.discover)

			else:
				self.params = MediaTypes.propertymap (self.discover)
				print self.params
				self.discoveredsignal.emit (self.row, MediaTypes.validate (self.params), self.params)

			self.contexttimer.stop()
			self.finished.emit()
