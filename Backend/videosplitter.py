#!/usr/bin/python

import os, subprocess
import gobject, gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler


class VideoSplitter (QtCore.QObject):

	updatemodel = QtCore.Signal (int, list)
	finished = QtCore.Signal()

	def __init__ (self, srcfile, dstfile, starttime, duration, title, row, parent = None):

		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.context = self.mainloop.get_context()

		self.srcfile = srcfile
		self.dstfile = dstfile
		self.starttime = starttime
		self.duration = duration
		self.title = title
		self.row = row

		self.status = (0, True)
		self.proc = None

	@QtCore.Slot()
	def startworker (self, username, time, filename, path):

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.contexthandler)
		self.contexttimer.start (100)

		self.sendnewsplitted (username, time, filename, path)

	def sendnewsplitted (self, username, time, filename, path):
		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)
		self.rpcworker.startnewsplitted.connect (self.rpcworker.newsplitted)
		self.rpcworker.newsplittedfinished.connect (self.rpc.quit)
		self.rpcworker.newsplittedfinished.connect (self.rpcworker.deleteLater)
		self.rpc.finished.connect (self.rpc.deleteLater)
		self.rpc.start()

		self.rpcworker.startnewsplitted.emit (username, time, filename, path)

	def contexthandler (self):
		if self.context.pending():
			self.context.iteration()

		self.doworks()

	def doworks (self):

		if self.status[0] == 0:

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", self.srcfile)
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", "tmp/raw.avi")
			progress = gst.element_factory_make ("progressreport")
#			progress.set_property ('silent', True)
			progress.set_property ('update-freq', 1)

			self.pipeline.add (source, progress, sink)
			gst.element_link_many (source, progress, sink)

			self.bus = self.pipeline.get_bus()
			self.bus.add_signal_watch()
			self.bus.enable_sync_message_emission()
			self.bus.connect ("message", self.on_message)
			self.bus.connect ("sync-message::element", self.on_sync_message)

			self.updatemodel.emit (self.row, (0, self.tr ("Not Started")))

			self.pipeline.set_state (gst.STATE_PLAYING)
			self.status = (1, False)

			return

		if self.status[0] == 1:
			if not self.status[1]:
				return

			if self.title:
				command = ["ffmpeg.exe", "-y", "-ss", self.starttime, "-t", self.duration,
					"-i", "tmp/raw.avi", "-metadata", "title=\"%s\"" % self.title, "-vcodec", "copy",
					"-acodec", "copy", "tmp/splitout.avi"]
			else:
				command = ["ffmpeg.exe", "-y", "-ss", self.starttime, "-t", self.duration,
						"-i", "tmp/raw.avi", "-vcodec", "copy", "-acodec", "copy", "tmp/splitout.avi"]

			print command

			self.proc = subprocess.Popen (command, shell = True)
			self.status = (2, False)
			return

		if self.status[0] == 2:
			if self.proc is None or self.proc.poll() is None:
				return

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", "tmp/splitout.avi")
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", self.dstfile)
			progress = gst.element_factory_make ("progressreport")
#			progress.set_property ('silent', True)
			progress.set_property ('update-freq', 1)

			self.pipeline.add (source, progress, sink)
			gst.element_link_many (source, progress, sink)

			self.bus = self.pipeline.get_bus()
			self.bus.add_signal_watch()
			self.bus.enable_sync_message_emission()
			self.bus.connect ("message", self.on_message)
			self.bus.connect ("sync-message::element", self.on_sync_message)

			self.pipeline.set_state (gst.STATE_PLAYING)
			self.status = (3, False)

		if self.status[0] == 3:
			if not self.status[1]:
				return

			tmpfile = os.path.join (os.getcwd(), "tmp/raw.avi")
			if os.path.exists (tmpfile):
				os.remove (tmpfile)
			tmpfile = os.path.join (os.getcwd(), "tmp/splitout.avi")
			if os.path.exists (tmpfile):
				os.remove (tmpfile)

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.status = (self.status[0], True)
			if self.status[0] == 3:
				self.updatemodel.emit (self.row, (100, self.tr ("Finished")))
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				if self.status[0] == 1:
					self.updatemodel.emit (self.row, (message.structure ['percent'] * 0.2, None))
				elif self.status[0] == 3:
					self.updatemodel.emit (self.row, (message.structure ['percent'] * 0.2 + 80, None))
					if message.structure ['percent'] >= 100:
						self.updatemodel.emit (self.row, (100, self.tr ("Finished")))

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
