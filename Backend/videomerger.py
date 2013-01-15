#!/usr/bin/python

import os, time, sys
import gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler


class VideoMerger (QtCore.QObject):

	startsignal = QtCore.Signal (unicode, unicode)
	cancelsignal = QtCore.Signal()
	appendtasksignal = QtCore.Signal (unicode, int)
	switchrowsignal = QtCore.Signal (int, int)
	removerowsignal = QtCore.Signal (int)
	updatemodel = QtCore.Signal (int, tuple)
	startnewmerge = QtCore.Signal (unicode, unicode)

	def __init__ (self, username, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.username = username
		self.parent = parent
		self.path = None
		self.srcfiles = []
		self.status = (0, 0, 0, False)
		self.proc = None

		self.bus = None

	@QtCore.Slot (unicode, int)
	def appendtask (self, srcfile, row):
		self.srcfiles.append ({'srcfile': srcfile, 'row': row})
		self.items = len (self.srcfiles)

	@QtCore.Slot (int, int)
	def switchrow (self, row1, row2):
		self.srcfiles[row1], self.srcfiles[row2] = self.srcfiles[row2], self.srcfiles[row1]

	@QtCore.Slot (int)
	def removerow (self, row):
		self.srcfiles.pop (row)
		self.items = len (self.srcfiles)

	@QtCore.Slot (unicode, unicode)
	def startworker (self, dstfile, path):

		if len (self.srcfiles) < 1:
			msg = QtGui.QMessageBox()
			msg.setInformativeText (self.tr ("Hasn't chosen any video clips."))
			msg.exec_()

			if os.path.exists (dstfile):
				os.remove (dstfile)

			return

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.contexthandler)
		self.contexttimer.start (100)

		self.dstfile = dstfile
		self.path = path

		self.status = (1, 0, 0, True)
		self.proc = None

		self.sendnewmerged (self.username, self.path)

	def sendnewmerged (self, username, path):
		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)
		self.rpcworker.newmergedfinished.connect (self.rpc.quit)
		self.rpcworker.newmergedfinished.connect (self.rpcworker.deleteLater)
		self.rpc.finished.connect (self.rpc.deleteLater)
		self.rpc.start()

		self.startnewmerge.connect (self.rpcworker.newmerged)
		self.startnewmerge.connect (self.parent.newmerged)
		self.startnewmerge.emit (self.username, self.path)

	@QtCore.Slot()
	def quitworker (self):
		self.pipeline.set_state (gst.STATE_NULL)
		self.contexttimer.stop()

	def doworks (self):

		if self.status[0] == 0 or self.status[0] > 9:
			return

		if self.status[0] == 1:
			self.status = (2, 0, self.items, True)
			return

		if self.status[0] == 2:
			if not self.status[3]:
				return

			i = self.status[1]
			if i < self.status[2]:

				self.updatemodel.emit (self.srcfiles[i - 1]['row'], (20, self.tr ("Preprocessed")))

				self.status = (self.status[0], self.status[1] + 1, self.status[2], False)

				self.srcfiles[i]['origname'] = "\\tmp\\orig%d.mpg" % (self.srcfiles[i]['row'])

				self.pipeline = gst.Pipeline ("pipeline")
				source = gst.element_factory_make ("filesrc")
				source.set_property ("location", self.srcfiles[i]['srcfile'])
				sink = gst.element_factory_make ("filesink")
				sink.set_property ("location", self.srcfiles[i]['origname'])
				progress = gst.element_factory_make ("progressreport")
				progress.set_property ('update-freq', 1)

				self.pipeline.add (source, progress, sink)
				gst.element_link_many (source, progress, sink)

				self.bus = self.pipeline.get_bus()

				self.pipeline.set_state (gst.STATE_PLAYING)
				return

			else:
				self.status = (3, 0, self.items, True)
				return

		if self.status[0] == 3:

			if self.status[3]:
				self.status = (self.status[0], self.status[1], self.status[2], False)

			else:

				if self.proc is None or not self.proc.state() == QtCore.QProcess.NotRunning:
					return

				print self.proc.readAllStandardOutput().data()
				print self.proc.readAllStandardError().data()
				self.proc = None

			i = self.status[1]
			if i < self.status[2]:

				self.updatemodel.emit (self.srcfiles[i]['row'], (40, self.tr ("Prerecoded")))

				self.status = (self.status[0], self.status[1] + 1, self.status[2], False)

				self.srcfiles[i]['recodename'] = "tmp\\recode%d.mpg" % (self.srcfiles[i]['row'])

				command = ["ffmpeg.exe", "-y", "-i", self.srcfiles[i]['origname'], "-b:a", "128000",
						"-b:v", "1024000", self.srcfiles[i]['recodename']]
				self.proc = QtCore.QProcess (self)
				self.proc.start (command.pop(0), command)

				return

			else:
				self.status = (4, 0, 0, True)
				self.proc = None
				return

		if self.status[0] == 4:

			if sys.platform == 'win32':
				command = ["cmd.exe", "/c"]
			else:
				command = []

			command.extend (["copy", "/y"])

			for i in xrange (self.items):

				if not i == 0:
					command.append ("+")

				command.append ("%s%s" % (self.srcfiles[i]['recodename'], "/b"))

			command.append ("tmp\\merged.mpg/b")

			print command

			self.proc = QtCore.QProcess (self)
			self.proc.start (command.pop(0), command)

			self.status = (5, 0, 0, True)
			return

		if self.status[0] == 5:
			if self.proc is None or not self.proc.state() == QtCore.QProcess.NotRunning:
				return

			print self.proc.readAllStandardOutput().data()
			print self.proc.readAllStandardError().data()
			self.proc = None

			for i in xrange (self.items):
				self.updatemodel.emit (i, (60, self.tr ("Merged")))

			self.status = (6, 0, 0, True)
			return

		if self.status[0] == 6:

			command = ["ffmpeg.exe", "-y", "-i", "tmp\\merged.mpg", "-b:a", "128000", "-b:v", "1024000",
				"tmp\\final.mpg"]
			self.proc = QtCore.QProcess (self)
			self.proc.start (command.pop(0), command)
			self.status = (7, 0, 0, True)
			return

		if self.status[0] == 7:
			if self.proc is None or not self.proc.state() == QtCore.QProcess.NotRunning:
				return

			print self.proc.readAllStandardOutput().data()
			print self.proc.readAllStandardError().data()
			self.proc = None

			for i in xrange (self.items):
				self.updatemodel.emit (i, (80, self.tr ("Recoded")))

			self.status = (8, 0, 0, True)

		if self.status[0] == 8:

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", "tmp\\final.mpg")
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", self.dstfile)
			progress = gst.element_factory_make ("progressreport")
			progress.set_property ('update-freq', 1)

			self.pipeline.add (source, progress, sink)
			gst.element_link_many (source, progress, sink)

			self.bus = self.pipeline.get_bus()

			self.pipeline.set_state (gst.STATE_PLAYING)
			self.status = (9, 0, 0, False)

		if self.status[0] == 9:
			if not self.status[3]:
				return

			for i in xrange (self.items):
				self.updatemodel.emit (i, (100, self.tr ("Finished")))

			self.status = (10, 0, 0, True)

			return

	def cb_pad_added (self, element, pad, islast):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked():
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)


	def contexthandler (self):

		while True:
			if not self.bus:
				break

			message = self.bus.poll (gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_ELEMENT, 0)
			if not message:
				break

			if message.type == gst.MESSAGE_EOS:
				self.pipeline.set_state(gst.STATE_NULL)
				self.status = (self.status[0], self.status[1], self.status[2], True)
			elif message.type == gst.MESSAGE_ERROR:
				self.pipeline.set_state(gst.STATE_NULL)
				err, debug = message.parse_error()
				print 'Error: %s' % err, debug
			elif message.type == gst.MESSAGE_ELEMENT:
				pass

		self.doworks()
