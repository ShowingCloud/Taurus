#!/usr/bin/python

import os, time, sys, re
import gst
from PySide import QtCore, QtGui

from Frontend import CommonError

class VideoMerger (QtCore.QObject):

	startsignal = QtCore.Signal (unicode, unicode)
	cancelsignal = QtCore.Signal()
	appendtasksignal = QtCore.Signal (unicode)
	verifiedtasksignal = QtCore.Signal (int, dict, bool)
	switchrowsignal = QtCore.Signal (int, int)
	removerowsignal = QtCore.Signal (int)
	updatemodel = QtCore.Signal (int, int)
	startnewmerge = QtCore.Signal (unicode)
	filenamedecided = QtCore.Signal (unicode)
	finished = QtCore.Signal()

	def __init__ (self, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.parent = parent
		self.path = None
		self.srcfiles = []

		self.bus = None
		self.params = None
		self.items = 0
		self.effectives = 0

		self.appendtasksignal.connect (self.appendtask)
		self.verifiedtasksignal.connect (self.verifiedtask)
		self.switchrowsignal.connect (self.switchrow)
		self.removerowsignal.connect (self.removerow)
		self.startsignal.connect (self.startworker)
		self.cancelsignal.connect (self.quitworker)
		QtGui.qApp.aboutToQuit.connect (self.quitworker)

	@QtCore.Slot (unicode)
	def appendtask (self, srcfile):
		self.srcfiles.append ({'srcfile': srcfile, 'effective': False})
		self.items = len (self.srcfiles)

	@QtCore.Slot (int, dict, bool)
	def verifiedtask (self, row, params, verified):

		self.srcfiles[row].update ({'effective': verified, 'params': params})
		self.srcfiles[row].update (params)

		if not verified:
			return

		num = 0
		for i in xrange (self.items):
			if self.srcfiles[i]['effective']:
				num += 1
		self.effectives = num

		if self.effectives == 1:
			self.params = params
		elif self.effectives > 1:
			if not self.checkcompat (self.params, params):
				self.srcfiles[self.items - 1]['effective'] = False
				self.effectives -= 1
				msg = CommonError (self.tr ("Media type not compatible."))
				msg.exec_()
				self.removerowsignal.emit (row)

	def checkcompat (self, common, new):

		if not common['muxer'] == new['muxer']:
			pass
#			return False
		if not common['videoheight'] == new['videoheight']:
			return False
		if not common['videowidth'] == new['videowidth']:
			return False
		if not common['videoframerate'] == new['videoframerate']:
			return False

		return True

	@QtCore.Slot (int, int)
	def switchrow (self, row1, row2):
		self.srcfiles[row1], self.srcfiles[row2] = self.srcfiles[row2], self.srcfiles[row1]

	@QtCore.Slot (int)
	def removerow (self, row):

		self.srcfiles[row]['effective'] = False

		num = 0
		params = None
		for i in xrange (self.items):
			if self.srcfiles[i]['effective']:
				num += 1
				if not params:
					params = self.srcfiles[i]['params']
		self.effectives = num
		self.params = params

	@QtCore.Slot (unicode, unicode)
	def startworker (self, filename, path):

		if not os.path.exists (path) or not os.path.isdir (path):
			msg = CommonError (self.tr ("Save destination invalid."))
			msg.exec_()
			return

		if len (self.srcfiles) < 1:
			msg = CommonError (self.tr ("Hasn't chosen any video clips."))
			msg.exec_()
			return

		dstfileinfo = QtCore.QFileInfo (os.path.join (path, filename))
		dstfile = QtCore.QDir.toNativeSeparators (dstfileinfo.absoluteFilePath())
		i = 0
		while os.path.exists (dstfile):
			i += 1
#			dstfile = os.path.join (dstfileinfo.absolutePath(), dstfileinfo.baseName() + "-%02d.%s" % (i, dstfileinfo.suffix()))
			dstfile = os.path.join (QtCore.QDir.toNativeSeparators (dstfileinfo.absolutePath()), dstfileinfo.baseName() + "-%02d.mp4" % i)
		os.close (os.open (dstfile, os.O_CREAT))
		dstfileinfo = QtCore.QFileInfo (dstfile)

		self.dstfile = QtCore.QDir.toNativeSeparators (dstfileinfo.absoluteFilePath())
		self.path = QtCore.QDir.toNativeSeparators (dstfileinfo.absolutePath())
		self.filenamedecided.emit (dstfileinfo.fileName())

		self.startnewmerge.emit (self.path)
		self.dowork()

	@QtCore.Slot()
	def quitworker (self):
		try:
			self.pipeline.set_state (gst.STATE_NULL)
		except:
			pass

	def dowork (self):

		self.pipeline = gst.Pipeline()
		vcomp = gst.element_factory_make ('gnlcomposition')
		vcomp.set_property ('async-handling', False)
		acomp = gst.element_factory_make ('gnlcomposition')
		acomp.set_property ('async-handling', False)
		vconv = gst.element_factory_make ('ffmpegcolorspace')
		vcomp.connect ("pad-added", self.comp_pad, vconv)
		aconv = gst.element_factory_make ('audioconvert')
		acomp.connect ("pad-added", self.comp_pad, aconv)
		vident = gst.element_factory_make ('identity')
		vident.set_property ('single-segment', True)
		vident.set_property ('sync', True)
		aident = gst.element_factory_make ('identity')
		aident.set_property ('single-segment', True)
		aident.set_property ('sync', True)
		vqueue = gst.element_factory_make ('queue2')
		aqueue = gst.element_factory_make ('queue2')

		'''
		vencode = gst.element_factory_make (self.srcfiles[0]['videoencoder'])
		if self.srcfiles[0]['videoencoder'] in ['x264enc']:
			index = 1
		else:
			index = 1000

		if self.srcfiles[0]['videobitrate']:
			try:
				vencode.set_property ('bitrate', round (float (self.srcfiles[0]['videobitrate']) / 1000) * index)
			except:
				vencode.set_property ('bitrate', 1024 * index)
		else:
			vencode.set_property ('bitrate', 1024 * index)

		aencode = gst.element_factory_make (self.srcfiles[0]['audioencoder'])
		if self.srcfiles[0]['audioencoder'] in ['lamemp3enc']:
			index = 1
		else:
			index = 1000

		if self.srcfiles[0]['audiobitrate']:
			try:
				aencode.set_property ('bitrate', round (float (self.srcfiles[0]['audiobitrate']) / 1000) * index)
			except:
				aencode.set_property ('bitrate', 128 * index)
		else:
			aencode.set_property ('bitrate', 128 * index)

		mux = gst.element_factory_make (self.srcfiles[0]['muxer'])
		'''

		vencode = gst.element_factory_make ('x264enc')
		vencode.set_property ('bitrate', 1024)
		aencode = gst.element_factory_make ('faac')
		aencode.set_property ('bitrate', 128000)
		mux = gst.element_factory_make ('mp4mux')

		preport = gst.element_factory_make ('progressreport', 'output')
		preport.set_property ('silent', False)
		preport.set_property ('update-freq', 1)
		sink = gst.element_factory_make ('filesink')
		sink.set_property ('location', self.dstfile)

		self.pipeline.add (vcomp, acomp, vconv, aconv, vident, aident, vqueue, aqueue, vencode, aencode, mux, preport, sink)
		gst.element_link_many (vconv, vident, vqueue, vencode, mux)
		gst.element_link_many (aconv, aident, aqueue, aencode, mux)
		gst.element_link_many (mux, preport, sink)

		timestamp = 0

		for i in xrange (self.items):

			if not self.srcfiles[i]['effective']:
				continue

			src = gst.Bin()
			source = gst.element_factory_make ('filesrc')
			source.set_property ('location', self.srcfiles[i]['srcfile'])
			preport = gst.element_factory_make ('progressreport', 'video %d' % i)
			preport.set_property ('silent', False)
			preport.set_property ('update-freq', 1)
			decode = gst.element_factory_make ('decodebin2')
			vconvert = gst.element_factory_make ('ffmpegcolorspace')
			fakesink = gst.element_factory_make ('fakesink')
			decode.connect ('pad-added', self.decode_pad, vconvert, fakesink)
			caps = gst.element_factory_make ('capsfilter')
			caps.set_property ('caps', self.srcfiles[i]['videooutcaps'])

			src.add_many (source, preport, decode, vconvert, caps, fakesink)
			gst.element_link_many (source, preport, decode)
			gst.element_link_many (vconvert, caps)
			src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

			vsrc = gst.element_factory_make ('gnlsource')
			vsrc.set_property ('start', timestamp)
			vsrc.set_property ('duration', self.srcfiles[i]['length'])
			vsrc.set_property ('media-start', 0)
			vsrc.set_property ('media-duration', self.srcfiles[i]['length'])
			vsrc.set_property ('priority', self.items - i)
			vsrc.set_property ('caps', self.srcfiles[i]['videooutcaps'])
			vsrc.set_property ('async-handling', False)
			vsrc.add (src)
			vcomp.add (vsrc)

			src = gst.Bin()
			source = gst.element_factory_make ('filesrc')
			source.set_property ('location', self.srcfiles[i]['srcfile'])
			preport = gst.element_factory_make ('progressreport', 'audio %d' % i)
			preport.set_property ('silent', False)
			preport.set_property ('update-freq', 1)
			decode = gst.element_factory_make ('decodebin2')
			aconvert = gst.element_factory_make ('audioconvert')
			fakesink = gst.element_factory_make ('fakesink')
			decode.connect ('pad-added', self.decode_pad, aconvert, fakesink)
			caps = gst.element_factory_make ('capsfilter')
			caps.set_property ('caps', self.srcfiles[i]['audiooutcaps'])

			src.add_many (source, preport, decode, aconvert, caps, fakesink)
			gst.element_link_many (source, preport, decode)
			gst.element_link_many (aconvert, caps)
			src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

			asrc = gst.element_factory_make ('gnlsource')
			asrc.set_property ('start', timestamp)
			asrc.set_property ('duration', self.srcfiles[i]['length'])
			asrc.set_property ('media-start', 0)
			asrc.set_property ('media-duration', self.srcfiles[i]['length'])
			asrc.set_property ('priority', self.items - i)
			asrc.set_property ('caps', self.srcfiles[i]['audiooutcaps'])
			asrc.set_property ('async-handling', False)
			asrc.add (src)
			acomp.add (asrc)

			timestamp += self.srcfiles[i]['length']

		src = gst.Bin()
		source = gst.element_factory_make ('videotestsrc')
		source.set_property ('pattern', 2)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', self.srcfiles[i]['videooutcaps'])

		src.add_many (source, caps)
		gst.element_link_many (source, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', 0)
		vsrc.set_property ('duration', timestamp)
		vsrc.set_property ('media-start', 0)
		vsrc.set_property ('media-duration', timestamp)
		vsrc.set_property ('priority', self.items * 10)
		vsrc.set_property ('caps', self.srcfiles[i]['videooutcaps'])
		vsrc.set_property ('async-handling', False)
		vsrc.add (src)
		vcomp.add (vsrc)

		src = gst.Bin()
		source = gst.element_factory_make ('audiotestsrc')
		source.set_property ('wave', 4)
		source.set_property ('volume', 0.0)
		source.set_property ('can-activate-pull', True)
		source.set_property ('can-activate-push', True)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', self.srcfiles[i]['audiooutcaps'])

		src.add_many (source, caps)
		gst.element_link_many (source, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', 0)
		asrc.set_property ('duration', timestamp)
		asrc.set_property ('media-start', 0)
		asrc.set_property ('media-duration', timestamp)
		asrc.set_property ('priority', self.items * 10)
		asrc.set_property ('caps', self.srcfiles[i]['audiooutcaps'])
		asrc.set_property ('async-handling', False)
		asrc.add (src)
		acomp.add (asrc)

		vcomp.set_property ('start', 0)
		vcomp.set_property ('duration', timestamp)
		vcomp.set_property ('media-duration', timestamp)
		acomp.set_property ('start', 0)
		acomp.set_property ('duration', timestamp)
		acomp.set_property ('media-duration', timestamp)

		self.bus = self.pipeline.get_bus()
		self.bus.enable_sync_message_emission()
		self.bus.add_signal_watch()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message", self.on_message)

		self.pipeline.set_state (gst.STATE_PLAYING)

	def comp_pad (self, comp, pad, nextcomp):
		nextpad = nextcomp.get_compatible_pad (pad, pad.get_caps())
		if nextpad and not nextpad.is_linked():
			pad.link (nextpad)

	def decode_pad (self, comp, pad, nextcomp, fakesink):
		nextpad = nextcomp.get_compatible_pad (pad, pad.get_caps())
		if nextpad and not nextpad.is_linked():
			pad.link (nextpad)
		else:
			nextpad = fakesink.get_pad ("sink")
			pad.link (nextpad)

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			print "EOS"
			self.pipeline.set_state (gst.STATE_NULL)
			self.updatemodel.emit (100, 100)
			self.finished.emit()
		elif message.type == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.pipeline.set_state (gst.STATE_NULL)
			self.updatemodel.emit (100, 100)
			self.finished.emit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
#				if 'output' in message.src.get_name():
				if 'video' in message.src.get_name() or 'audio' in message.src.get_name():
					try:
						num = int (re.findall (r'\d+', message.src.get_name())[0])
						progress = message.structure ['percent']
						self.updatemodel.emit (num, progress)
					except:
						print "error processing"
