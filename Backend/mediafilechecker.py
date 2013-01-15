#!/usr/bin/python

import os
import gobject, gst
from gst.extend import discoverer
from PySide import QtCore, QtGui


class MediaFileChecker (QtCore.QObject):

	discoveredsignal = QtCore.Signal (int, list)

	def __init__ (self, mediafile, row, parent = None):
		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.context = self.mainloop.get_context()

		self.mediafile = mediafile
		self.row = row

	@QtCore.Slot()
	def startworker (self):

		contexttimer = QtCore.QTimer()
		contexttimer.timeout.connect (lambda: self.context.pending() and self.context.iteration())
		contexttimer.start (100)

		if not os.path.isfile (self.mediafile):
			self.discoveredsignal.emit (self.row, (None, None, None))
			self.finished.emit()
			return

		d = discoverer.Discoverer (self.mediafile)
		d.connect ("discovered", self.on_discovered)
		d.discover()

	def on_discovered (self, d, is_media):

		if is_media and d.is_video:

			print "v %s : %s X %s @ %s / %s %s" % (d.videocaps, d.videowidth, d.videoheight,
					d.videorate.num, d.videorate.denom, d.videolength)
			if d.is_audio:
				print "a %s : %s X %s X %s @ %s %s %s" % (d.audiocaps, d.audiowidth,
						d.audiodepth, d.audiochannels, d.audiorate,
						d.audiolength, d.audiofloat and 'fp' or 'int')

			self.discoveredsignal.emit (self.row, (d.videowidth, d.videoheight, d.videolength))

		else:
			print "Not video or not audio"
			self.discoveredsignal.emit (self.row, (None, None, None))
