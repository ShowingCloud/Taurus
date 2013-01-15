#!/usr/bin/python

import os, subprocess
import gobject, gst
from PySide import QtCore, QtGui


class VideoSplitter (QtCore.QObject):

	updatemodel = QtCore.Signal (int, list)
	finished = QtCore.Signal()

	def __init__ (self, srcfile, dstfile, starttime, duration, row, parent = None):

		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.srcfile = srcfile
		self.dstfile = dstfile
		self.starttime = starttime
		self.duration = duration
		self.row = row
		self.procedure = 0

		QtGui.qApp.aboutToQuit.connect (self.quitworker)

	@QtCore.Slot()
	def startworker (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.srcfile)
		sink = gst.element_factory_make ("filesink")
		sink.set_property ("location", "tmp/raw.avi")
		progress = gst.element_factory_make ("progressreport")
#		progress.set_property ('silent', True)
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
		self.procedure = 1
		self.mainloop.run()
		self.pipeline.set_state (gst.STATE_NULL)

		if subprocess.call (["ffmpeg.exe", "-y", "-ss", self.starttime, "-t", self.duration, "-i", "tmp/raw.avi", "-vcodec", "copy", "-acodec", "copy", "tmp/splitout.avi"], shell = True) != 0:
			print "Error when splitting video using ffmpeg"
			return

		self.procedure = 2

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", "tmp/splitout.avi")
		sink = gst.element_factory_make ("filesink")
		sink.set_property ("location", self.dstfile)
		progress = gst.element_factory_make ("progressreport")
#		progress.set_property ('silent', True)
		progress.set_property ('update-freq', 1)

		self.pipeline.add (source, progress, sink)
		gst.element_link_many (source, progress, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.pipeline.set_state (gst.STATE_PLAYING)
		self.procedure = 3
		self.mainloop.run()
		self.pipeline.set_state (gst.STATE_NULL)

		tmpfile = os.path.join (os.getcwd(), "tmp/raw.avi")
		if os.path.exists (tmpfile):
			os.remove (tmpfile)
		tmpfile = os.path.join (os.getcwd(), "tmp/splitout.avi")
		if os.path.exists (tmpfile):
			os.remove (tmpfile)

		self.finished.emit()

	@QtCore.Slot()
	def quitworker (self):
		if self.mainloop.is_running():
			self.mainloop.quit()

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			if self.procedure == 3:
				self.updatemodel.emit (self.row, (100, self.tr ("Finished")))
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				if self.procedure == 1:
					self.updatemodel.emit (self.row, (message.structure ['percent'] * 0.2, None))
				elif self.procedure == 3:
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
