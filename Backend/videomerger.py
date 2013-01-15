#!/usr/bin/python

import os, subprocess
import gobject, gst
from PySide import QtCore, QtGui


class VideoMerger (QtCore.QObject):

	finished = QtCore.Signal()
	startsignal = QtCore.Signal (unicode, unicode)
	appendtasksignal = QtCore.Signal (unicode, int)
	switchrowsignal = QtCore.Signal (int, int)
	removerowsignal = QtCore.Signal (int)
	updatemodel = QtCore.Signal (int, list)

	def __init__ (self, parent = None):

		QtCore.QObject.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()

		self.srcfiles = []

		QtGui.qApp.aboutToQuit.connect (self.quitworker)

	@QtCore.Slot (unicode, int)
	def appendtask (self, srcfile, row):
		self.srcfiles.append ({'srcfile': srcfile, 'row': row})
		self.items = len (self.srcfiles)

	@QtCore.Slot (int, int)
	def switchrow (self, row1, row2):
		rows = [i['row'] for i in self.srcfiles]
		a, b = rows.index (row1), rows.index (row2)
		self.srcfiles[a], self.srcfiles[b] = self.srcfiles[b], self.srcfiles[a]

	@QtCore.Slot (int)
	def removerow (self, row):
		rows = [i['row'] for i in self.srcfiles]
		r = rows.index (row)
		self.srcfiles.pop (r)
		self.items = len (self.srcfiles)

	@QtCore.Slot (unicode, unicode)
	def startworker (self, filename, path):

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

		for i in xrange (self.items):

			self.srcfiles[i]['origname'] = "tmp/orig%d.avi" % (self.srcfiles[i]['row'])

			self.pipeline = gst.Pipeline ("pipeline")
			source = gst.element_factory_make ("filesrc")
			source.set_property ("location", self.srcfiles[i]['srcfile'])
			sink = gst.element_factory_make ("filesink")
			sink.set_property ("location", self.srcfiles[i]['origname'])
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
			self.mainloop.run()
			self.pipeline.set_state (gst.STATE_NULL)

			self.updatemodel.emit (self.srcfiles[i]['row'], (20, self.tr ("Preprocessed")))

		for i in xrange (self.items):

			self.srcfiles[i]['recodename'] = "tmp/recode%d.avi" % (self.srcfiles[i]['row'])

			if subprocess.call (["ffmpeg.exe", "-y", "-i", self.srcfiles[i]['origname'], "-b:a", "128000", "-b:v", "1024000", self.srcfiles[i]['recodename']], shell = True) != 0:
				print "Error when preprocessing video: %s" % self.srcfiles[i]['origname']
				return

			self.updatemodel.emit (self.srcfiles[i]['row'], (40, self.tr ("Prerecoded")))

		command = ["copy", "/y"]
		rows = [i['row'] for i in self.srcfiles]

		for i in xrange (self.items):

			if not i == 0:
				command.append ("+")

			r = rows.index (i)
			command.append ("%s%s" % (self.srcfiles[r]['recodename'].replace ('/', '\\'), "/b"))

		command.append ("tmp\\merged.avi/b")

		print command

		if subprocess.call (command, shell = True) != 0:
			print "Error copying file together"
			return

		for i in xrange (self.items):
			self.updatemodel.emit (i, (60, self.tr ("Merged")))

		if subprocess.call (["ffmpeg.exe", "-y", "-i", "tmp/merged.avi", "-b:a", "128000", "-b:v", "1024000", "tmp/final.avi"], shell = True) != 0:
			print "Error when processing output video"
			return

		for i in xrange (self.items):
			self.updatemodel.emit (i, (80, self.tr ("Recoded")))

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", "tmp/final.avi")
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
		self.mainloop.run()
		self.pipeline.set_state (gst.STATE_NULL)

		for i in xrange (self.items):
			self.updatemodel.emit (i, (100, self.tr ("Finished")))

#		tmpfile = os.path.join (os.getcwd(), "tmp/raw.avi")
#		if os.path.exists (tmpfile):
#			os.remove (tmpfile)
#		tmpfile = os.path.join (os.getcwd(), "tmp/splitout.avi")
#		if os.path.exists (tmpfile):
#			os.remove (tmpfile)

		self.finished.emit()

	@QtCore.Slot()
	def quitworker (self):
		if self.mainloop.is_running():
			self.mainloop.quit()

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.mainloop.quit()
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
