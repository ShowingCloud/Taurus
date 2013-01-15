#!/usr/bin/python

import os
import gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler


class VideoSplitter (QtCore.QObject):

	updatemodel = QtCore.Signal (int)
	finished = QtCore.Signal()
	startnewsplit = QtCore.Signal (unicode, unicode, unicode, unicode)
	addtranscode = QtCore.Signal (unicode)

	def __init__ (self, srcfile, dstfile, starttime, duration, title, totranscode, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.srcfile = srcfile
		self.dstfile = dstfile
		self.starttime = starttime
		self.duration = duration
		self.title = title
		self.totranscode = totranscode
		self.parent = parent

		self.bus = None

	@QtCore.Slot()
	def startworker (self, username, time, filename, path):

		self.status = (0, True)
		self.proc = None

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.contexthandler)
		self.contexttimer.start (100)

		self.sendnewsplitted (username, time, filename, path)

	def sendnewsplitted (self, username, time, filename, path):

		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)
		self.rpcworker.newsplittedfinished.connect (self.rpc.quit)
		self.rpcworker.newsplittedfinished.connect (self.rpcworker.deleteLater)
		self.rpc.finished.connect (self.rpc.deleteLater)
		self.rpc.start()

		self.startnewsplit.connect (self.rpcworker.newsplitted)
		self.startnewsplit.connect (self.parent.newsplitted)
		self.startnewsplit.emit (username, time, filename, path)

	def contexthandler (self):

		while True:
			if not self.bus:
				break

			message = self.bus.poll (gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_ELEMENT, 0)
			if not message:
				break

			if message.type == gst.MESSAGE_EOS:
				self.pipeline.set_state(gst.STATE_NULL)
				self.status = (self.status[0], True)
				if self.status[0] == 3:
					self.updatemodel.emit (100)
			elif message.type == gst.MESSAGE_ERROR:
				self.pipeline.set_state(gst.STATE_NULL)
				err, debug = message.parse_error()
				print 'Error: %s' % err, debug
			elif message.type == gst.MESSAGE_ELEMENT:
				if message.structure.get_name() == "progress":
					if self.status[0] == 1:
						self.updatemodel.emit (message.structure ['percent'] * 0.2)
					elif self.status[0] == 3:
						self.updatemodel.emit (message.structure ['percent'] * 0.2 + 80)
						if message.structure ['percent'] >= 100:
							self.updatemodel.emit (100)

		self.doworks()

	def doworks (self):

		if self.status[0] == 0:

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", self.srcfile)
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", "tmp\\raw.avi")
			progress = gst.element_factory_make ("progressreport")
			progress.set_property ('update-freq', 1)

			self.pipeline.add (source, progress, sink)
			gst.element_link_many (source, progress, sink)

			self.bus = self.pipeline.get_bus()

			self.updatemodel.emit (0)

			self.pipeline.set_state (gst.STATE_PLAYING)
			self.status = (1, False)

			return

		if self.status[0] == 1:
			if not self.status[1]:
				return

			command = ["ffmpeg.exe", "-y", "-ss", self.starttime, "-t", self.duration, "-i", "tmp\\raw.avi"]

			if self.title:
				command.extend (["-metadata", "title=%s" % self.title])

			command.extend (["-vcodec", "copy", "-acodec", "copy", "tmp\\splitout.avi"])

			self.proc = QtCore.QProcess (self)
			self.proc.start (command.pop(0), command)

			self.status = (2, False)
			return

		if self.status[0] == 2:
			if self.proc is None or not self.proc.state() == QtCore.QProcess.NotRunning:
				return

			print self.proc.readAllStandardOutput().data()
			print self.proc.readAllStandardError().data()
			self.proc = None

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", "tmp\\splitout.avi")
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", self.dstfile)
			progress = gst.element_factory_make ("progressreport")
			progress.set_property ('update-freq', 1)

			self.pipeline.add (source, progress, sink)
			gst.element_link_many (source, progress, sink)

			self.bus = self.pipeline.get_bus()

			self.pipeline.set_state (gst.STATE_PLAYING)
			self.status = (3, False)

		if self.status[0] == 3:
			if not self.status[1]:
				return

			if self.totranscode:
				self.addtranscode.emit (self.dstfile)

			self.finished.emit()

	def cb_pad_added (self, element, pad, islast):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked():
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)
