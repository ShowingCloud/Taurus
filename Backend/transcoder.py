#!/usr/bin/python

import gobject, gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler


class Transcoder (QtCore.QObject):

	updatemodel = QtCore.Signal (int, list)
	playsignal = QtCore.Signal()
	pausesignal = QtCore.Signal()
	removesignal = QtCore.Signal()

	def __init__ (self, srcfile, dstfile, username, path, row, parent = None):

		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.context = self.mainloop.get_context()

		self.srcfile = srcfile
		self.dstfile = dstfile
		self.row = row
		self.username = username
		self.path = path

		QtGui.qApp.aboutToQuit.connect (self.remove)

	@QtCore.Slot()
	def startworker (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.srcfile)
		decoder = gst.element_factory_make ("decodebin2")
		decoder.connect ("new-decoded-pad", self.cb_pad_added)
		queuea = gst.element_factory_make ("queue")
		queuev = gst.element_factory_make ("queue")
		videoscale = gst.element_factory_make ("videoscale")
		videorate = gst.element_factory_make ("videorate")
		audioconv = gst.element_factory_make ("audioconvert")
		colorspace = gst.element_factory_make ("ffmpegcolorspace")
		colorspace2 = gst.element_factory_make ("ffmpegcolorspace")
		caps = gst.element_factory_make ("capsfilter")
		caps.set_property ('caps', gst.caps_from_string ("video/x-raw-rgb, width=640, height=480, framerate=25/1"))
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

		self.__apad = queuea.get_pad ("sink")
		self.__vpad = queuev.get_pad ("sink")

		self.pipeline.add (source, decoder, queuea, queuev, audioenc, videoenc, muxer, progress, sink, colorspace, caps, videoscale, videorate, audioconv, colorspace2)
		gst.element_link_many (source, decoder)
		gst.element_link_many (queuev, videoscale, videorate, colorspace, caps, colorspace2, videoenc, muxer)
		gst.element_link_many (queuea, audioconv, audioenc, muxer)
		gst.element_link_many (muxer, progress, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect (lambda: self.context.pending() and self.context.iteration())
		self.timer.start (100)

		self.pipeline.set_state (gst.STATE_PLAYING)

		self.sendnewtransferred (self.username, self.path)

	def sendnewtransferred (self, username, path):
		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)
		self.rpcworker.startnewtransferred.connect (self.rpcworker.newtransferred)
		self.rpcworker.newtransferredfinished.connect (self.rpc.quit)
		self.rpcworker.newtransferredfinished.connect (self.rpcworker.deleteLater)
		self.rpc.finished.connect (self.rpc.deleteLater)
		self.rpc.start()

		self.rpcworker.startnewtransferred.emit (self.username, self.path)

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

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.updatemodel.emit (self.row, (100, self.tr ("Finished")))
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				self.updatemodel.emit (self.row, (message.structure ['percent'], None))

	def on_sync_message (self, bus, message):
		if message.structure is None:
			return
		message_name = message.structure.get_name()

	def cb_pad_added (self, element, pad, islast):
	    caps = pad.get_caps()
	    name = caps[0].get_name()
	    if 'audio' in name:
	        if not self.__apad.is_linked(): # Only link once
	            pad.link (self.__apad)
	    elif 'video' in name:
	        if not self.__vpad.is_linked():
	            pad.link (self.__vpad)
