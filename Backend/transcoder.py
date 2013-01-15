#!/usr/bin/python

import os
import gst
from PySide import QtCore, QtGui


class Transcoder (QtCore.QObject):

	updatemodel = QtCore.Signal (int, tuple)
	playsignal = QtCore.Signal()
	pausesignal = QtCore.Signal()
	removesignal = QtCore.Signal()
	startnewtransfer = QtCore.Signal (unicode, unicode)
	finished = QtCore.Signal()

	def __init__ (self, srcfile, path, row, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.srcfile = srcfile
		self.row = row
		self.path = path
		self.parent = parent

		srcfileinfo = QtCore.QFileInfo (srcfile)
		self.srcpath = QtCore.QDir.toNativeSeparators (srcfileinfo.absolutePath())
		dstfile = os.path.join (path, srcfileinfo.baseName() + ".mp4")
		i = 0
		while os.path.exists (dstfile):
			i += 1
			dstfile = os.path.join (path, srcfileinfo.baseName() + "-%02d.mp4" % i)
		os.close (os.open (dstfile, os.O_CREAT))
		dstfileinfo = QtCore.QFileInfo (dstfile)
		self.dstfile = QtCore.QDir.toNativeSeparators (dstfileinfo.absoluteFilePath())

		QtGui.qApp.aboutToQuit.connect (self.remove)

	@QtCore.Slot()
	def startworker (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.srcfile)
		decoder = gst.element_factory_make ("decodebin2")
		decoder.connect ("pad-added", self.cb_pad_added)
		videoscale = gst.element_factory_make ("videoscale")
		videorate = gst.element_factory_make ("videorate")
		videoconv = gst.element_factory_make ("ffmpegcolorspace")
		audioconv = gst.element_factory_make ("audioconvert")
		caps = gst.element_factory_make ("capsfilter")
		caps.set_property ('caps', gst.caps_from_string ("\
			video/x-raw-yuv, width=640, height=480, framerate=25/1;\
			video/x-raw-rgb, width=640, height=480, framerate=25/1"))
		audioenc = gst.element_factory_make ("faac")
		audioenc.set_property ('bitrate', 128000)
		videoenc = gst.element_factory_make ("x264enc")
		videoenc.set_property ('bitrate', 1024)
		muxer = gst.element_factory_make ("mp4mux")
		sink = gst.element_factory_make ("filesink")
		sink.set_property ("location", self.dstfile)
		progress = gst.element_factory_make ("progressreport")
		progress.set_property ('silent', True)
		progress.set_property ('update-freq', 1)

		self.__apad = audioconv.get_pad ("sink")
		self.__vpad = videoscale.get_pad ("sink")

		self.pipeline.add (source, decoder, audioenc, videoenc, muxer, progress, sink,
				caps, videoscale, videorate, audioconv, videoconv)
		gst.element_link_many (source, decoder)
		gst.element_link_many (videoscale, videorate, videoconv, caps, videoenc, muxer)
		gst.element_link_many (audioconv, audioenc, muxer)
		gst.element_link_many (muxer, progress, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect ("message", self.on_message)

		self.pipeline.set_state (gst.STATE_PLAYING)
		self.updatemodel.emit (self.row, (None, self.tr ("Transcoding...")))

		self.startnewtransfer.emit (self.path, self.srcpath)

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.updatemodel.emit (self.row, (100, self.tr ("Finished")))
			self.finished.emit()
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.finished.emit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				self.updatemodel.emit (self.row, (message.structure ['percent'], None))

	@QtCore.Slot()
	def play (self):
		self.pipeline.set_state (gst.STATE_PLAYING)
		self.updatemodel.emit (self.row, (None, self.tr ("Transcoding...")))

	@QtCore.Slot()
	def pause (self):
		self.pipeline.set_state (gst.STATE_PAUSED)
		self.updatemodel.emit (self.row, (None, self.tr ("Paused")))

	@QtCore.Slot()
	def remove (self):
		self.pipeline.set_state (gst.STATE_NULL)
		self.finished.emit()

	def cb_pad_added (self, element, pad):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked():
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)
