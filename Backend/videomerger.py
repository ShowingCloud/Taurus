#!/usr/bin/python

import os, subprocess, time
import gobject, gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler


class VideoMerger (QtCore.QObject):

	startsignal = QtCore.Signal (unicode, unicode)
	cancelsignal = QtCore.Signal()
	appendtasksignal = QtCore.Signal (unicode, int)
	switchrowsignal = QtCore.Signal (int, int)
	removerowsignal = QtCore.Signal (int)
	updatemodel = QtCore.Signal (int, list)

	def __init__ (self, username, parent = None):

		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.context = self.mainloop.get_context()

		self.username = username
		self.path = None
		self.srcfiles = []
		self.status = (0, 0, 0, False)
		self.proc = None

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
	def startworker (self, filename, path):

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.contexthandler)
		self.contexttimer.start (100)

		if len (self.srcfiles) < 1:
			msg = QtGui.QMessageBox()
			msg.setInformativeText (self.tr ("Hasn't chosen any video clips."))
			msg.exec_()
			return

		if path == "" or filename == "" or not os.path.exists (path) or not os.path.isdir (path):
			msg = QtGui.QMessageBox()
			msg.setInformativeText (self.tr ("Save destination invalid."))
			msg.exec_()
			return

		self.dstfile = os.path.join (path, filename)
		self.path = path

		self.status = (1, 0, 0, True)

		self.sendnewmerged (self.username, self.path)

	def sendnewmerged (self, username, path):
		self.rpcworker = RPCHandler()
		self.rpc = QtCore.QThread()
		self.rpcworker.moveToThread (self.rpc)
		self.rpcworker.startnewmerged.connect (self.rpcworker.newmerged)
		self.rpcworker.newmergedfinished.connect (self.rpc.quit)
		self.rpcworker.newmergedfinished.connect (self.rpcworker.deleteLater)
		self.rpc.finished.connect (self.rpc.deleteLater)
		self.rpc.start()

		self.rpcworker.startnewmerged.emit (self.username, self.path)

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

				self.srcfiles[i]['origname'] = "tmp/orig%d.mpg" % (self.srcfiles[i]['row'])

				self.pipeline = gst.Pipeline ("pipeline")
				source = gst.element_factory_make ("filesrc")
				source.set_property ("location", self.srcfiles[i]['srcfile'])
				sink = gst.element_factory_make ("filesink")
				sink.set_property ("location", self.srcfiles[i]['origname'])
				progress = gst.element_factory_make ("progressreport")
#				progress.set_property ('silent', True)
				progress.set_property ('update-freq', 1)

				self.pipeline.add (source, progress, sink)
				gst.element_link_many (source, progress, sink)

				self.bus = self.pipeline.get_bus()
				self.bus.add_signal_watch()
				self.bus.enable_sync_message_emission()
				self.bus.connect ("message", self.on_message)
				self.bus.connect ("sync-message::element", self.on_sync_message)

				self.pipeline.set_state (gst.STATE_PLAYING)
				return

			else:
				self.status = (3, 0, self.items, True)
				return

		if self.status[0] == 3:
			if self.proc is None or self.proc.poll() is None:
				if self.status[3]:
					self.status = (self.status[0], self.status[1], self.status[2], False)
				else:
					return

			i = self.status[1]
			if i < self.status[2]:

				self.updatemodel.emit (self.srcfiles[i]['row'], (40, self.tr ("Prerecoded")))

				self.status = (self.status[0], self.status[1] + 1, self.status[2], False)

				self.srcfiles[i]['recodename'] = "tmp/recode%d.mpg" % (self.srcfiles[i]['row'])

				self.proc = subprocess.Popen (["ffmpeg.exe", "-y", "-i", self.srcfiles[i]['origname'],
					"-b:a", "128000", "-b:v", "1024000", self.srcfiles[i]['recodename']], shell = True)
				return

			else:
				self.status = (4, 0, 0, True)
				self.proc = None
				return

		if self.status[0] == 4:

			command = ["copy", "/y"]
			rows = [i['row'] for i in self.srcfiles]

			for i in xrange (self.items):

				if not i == 0:
					command.append ("+")

				r = rows.index (i)
				command.append ("%s%s" % (self.srcfiles[r]['recodename'].replace ('/', '\\'), "/b"))

			command.append ("tmp\\merged.mpg/b")

			print command

			self.proc = subprocess.Popen (command, shell = True)
			self.status = (5, 0, 0, True)
			return

		if self.status[0] == 5:
			if self.proc == None or self.proc.poll() == None:
				return

			for i in xrange (self.items):
				self.updatemodel.emit (i, (60, self.tr ("Merged")))

			self.status = (6, 0, 0, True)
			return

		if self.status[0] == 6:

			self.proc = subprocess.Popen (["ffmpeg.exe", "-y", "-i", "tmp/merged.mpg", "-b:a", "128000", "-b:v", "1024000",
				"tmp/final.mpg"], shell = True)
			self.status = (7, 0, 0, True)
			return

		if self.status[0] == 7:
			if self.proc == None or self.proc.poll() == None:
				return

			for i in xrange (self.items):
				self.updatemodel.emit (i, (80, self.tr ("Recoded")))

			self.status = (8, 0, 0, True)

		if self.status[0] == 8:

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", "tmp/final.mpg")
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
			self.status = (9, 0, 0, False)

		if self.status[0] == 9:
			if not self.status[3]:
				return

			for i in xrange (self.items):
				self.updatemodel.emit (i, (100, self.tr ("Finished")))

			self.status = (10, 0, 0, True)

			return

#		tmpfile = os.path.join (os.getcwd(), "tmp/raw.avi")
#		if os.path.exists (tmpfile):
#			os.remove (tmpfile)
#		tmpfile = os.path.join (os.getcwd(), "tmp/splitout.avi")
#		if os.path.exists (tmpfile):
#			os.remove (tmpfile)

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.status = (self.status[0], self.status[1], self.status[2], True)
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
		elif message.type == gst.MESSAGE_ELEMENT:
			pass

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


	def contexthandler (self):
		if self.context.pending():
			self.context.iteration()

		self.doworks()

