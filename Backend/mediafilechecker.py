#!/usr/bin/python

import os

import gobject, gst
from gst import pbutils
from PySide import QtCore, QtGui


class MediaFileChecker (QtCore.QObject):

	discoveredsignal = QtCore.Signal (int, list)
	finished = QtCore.Signal()

	def __init__ (self, mediafile, row, parent = None):
		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mediafile = mediafile
		self.row = row

	@QtCore.Slot()
	def startworker (self):

		if not os.path.isfile (self.mediafile):
			self.discoveredsignal.emit (self.row, (None, None, None))
			self.finished.emit()
			return

		d = gst.pbutils.Discoverer (50000000000)
		info = d.discover_uri ("file:///" + self.mediafile)

		self.streaminfo = info.get_stream_info()
		self.duration = info.get_duration()
		self.container = self.streaminfo.get_caps()

		print "container: " + gst.pbutils.get_codec_description (self.container)

		audiostreams = info.get_audio_streams()

		for i in audiostreams:
			self.audiocaps = i.get_caps()
			self.audiotags = i.get_tags()
			print "audio stream: " + gst.pbutils.get_codec_description (self.audiocaps)

		videostreams = info.get_video_streams()

		if len (videostreams) == 0:
			self.discoveredsignal.emit (self.row, (None, None, None))

		for i in videostreams:
			self.videocaps = i.get_caps()
			self.videotags = i.get_tags()
			self.videoheight = gst.pbutils.gst_discoverer_video_info_get_height (i)
			self.videowidth = gst.pbutils.gst_discoverer_video_info_get_width (i)
			print "video stream: " + gst.pbutils.get_codec_description (self.videocaps)
			print "%d X %d" % (self.videowidth, self.videoheight)

		print "duration: %d" % self.duration

		self.discoveredsignal.emit (self.row, (self.videowidth, self.videoheight, self.duration))

		self.finished.emit()
