#!/usr/bin/python

import os, time, sys, re
import gst
from PySide import QtCore, QtGui

from Toolkit import RPCHandler

class VideoMerger (QtCore.QObject):

	startsignal = QtCore.Signal (unicode, unicode)
	cancelsignal = QtCore.Signal()
	appendtasksignal = QtCore.Signal (dict, unicode, int)
	switchrowsignal = QtCore.Signal (int, int)
	removerowsignal = QtCore.Signal (int)
	updatemodel = QtCore.Signal (int, int)
	startnewmerge = QtCore.Signal (unicode, unicode)

	def __init__ (self, username, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.username = username
		self.parent = parent
		self.path = None
		self.srcfiles = []

		self.bus = None

	@QtCore.Slot (unicode, int)
	def appendtask (self, params, srcfile, row):
		self.srcfiles.append (dict ([('srcfile', srcfile), ('row', row)] + params.items()))
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

		self.dstfile = dstfile
		self.path = path

		self.dowork()
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

	def dowork (self):

		self.pipeline = gst.Pipeline()
		vcomp = gst.element_factory_make ('gnlcomposition')
		acomp = gst.element_factory_make ('gnlcomposition')
		vconv = gst.element_factory_make ('ffmpegcolorspace')
		vcomp.connect ("pad-added", self.comp_pad, vconv)
		aconv = gst.element_factory_make ('audioconvert')
		acomp.connect ("pad-added", self.comp_pad, aconv)
		vident = gst.element_factory_make ('identity')
		vident.set_property ('single-segment', True)
		aident = gst.element_factory_make ('identity')
		aident.set_property ('single-segment', True)

		vencode = gst.element_factory_make (self.srcfiles[0]['videoencoder'])
		if self.srcfiles[0]['videobitrate']:
			try:
				vencode.set_property ('bitrate', round (float (self.srcfiles[0]['videobitrate']) / 1000) * 1000)
			except:
				vencode.set_property ('bitrate', 1024000)
		else:
			vencode.set_property ('bitrate', 1024000)

		aencode = gst.element_factory_make (self.srcfiles[0]['audioencoder'])
		if self.srcfiles[0]['audiobitrate']:
			try:
				aencode.set_property ('bitrate', round (float (self.srcfiles[0]['audiobitrate']) / 1000) * 1000)
			except:
				aencode.set_property ('bitrate', 128000)
		else:
			aencode.set_property ('bitrate', 128000)

		mux = gst.element_factory_make (self.srcfiles[0]['muxer'])
		sink = gst.element_factory_make ('filesink')
		sink.set_property ('location', self.dstfile)

		timestamp = 0

		for i in xrange (self.items):

			src = gst.Bin()
			source = gst.element_factory_make ('filesrc')
			source.set_property ('location', self.srcfiles[i]['srcfile'])
			preport = gst.element_factory_make ('progressreport', 'report %d' % i)
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
			vsrc.add (src)
			vcomp.add (vsrc)

			src = gst.Bin()
			source = gst.element_factory_make ('filesrc')
			source.set_property ('location', self.srcfiles[i]['srcfile'])
			decode = gst.element_factory_make ('decodebin2')
			aconvert = gst.element_factory_make ('audioconvert')
			fakesink = gst.element_factory_make ('fakesink')
			decode.connect ('pad-added', self.decode_pad, aconvert, fakesink)
			caps = gst.element_factory_make ('capsfilter')
			caps.set_property ('caps', self.srcfiles[i]['audiooutcaps'])

			src.add_many (source, decode, aconvert, caps, fakesink)
			gst.element_link_many (source, decode)
			gst.element_link_many (aconvert, caps)
			src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

			asrc = gst.element_factory_make ('gnlsource')
			asrc.set_property ('start', timestamp)
			asrc.set_property ('duration', self.srcfiles[i]['length'])
			asrc.set_property ('media-start', 0)
			asrc.set_property ('media-duration', self.srcfiles[i]['length'])
			asrc.set_property ('priority', self.items - i)
			asrc.set_property ('caps', self.srcfiles[i]['audiooutcaps'])
			asrc.add (src)
			acomp.add (asrc)

			timestamp += self.srcfiles[i]['length']

		src = gst.Bin()
		source = gst.element_factory_make ('videotestsrc')
		source.set_property ('pattern', 2)
		preport = gst.element_factory_make ('progressreport', 'final')
		preport.set_property ('silent', False)
		preport.set_property ('update-freq', 1)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', self.srcfiles[i]['videooutcaps'])

		src.add_many (source, preport, caps)
		gst.element_link_many (source, preport, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', timestamp)
		vsrc.set_property ('duration', 1 * gst.SECOND)
#		vsrc.set_property ('media-start', 0)
		vsrc.set_property ('media-duration', 1 * gst.SECOND)
		vsrc.set_property ('priority', self.items * 10)
		vsrc.set_property ('caps', self.srcfiles[i]['videooutcaps'])
		vsrc.add (src)
		vcomp.add (vsrc)

		src = gst.Bin()
		source = gst.element_factory_make ('audiotestsrc')
		source.set_property ('wave', 4)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', self.srcfiles[i]['audiooutcaps'])

		src.add_many (source, caps)
		gst.element_link_many (source, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', timestamp)
		asrc.set_property ('duration', 1 * gst.SECOND)
#		asrc.set_property ('media-start', 0)
		asrc.set_property ('media-duration', 1 * gst.SECOND)
		asrc.set_property ('priority', self.items * 10)
		asrc.set_property ('caps', self.srcfiles[i]['audiooutcaps'])
		asrc.add (src)
		acomp.add (asrc)

		vcomp.set_property ('start', 0)
		vcomp.set_property ('duration', timestamp)
		vcomp.set_property ('media-duration', timestamp)
		acomp.set_property ('start', 0)
		acomp.set_property ('duration', timestamp)
		acomp.set_property ('media-duration', timestamp)

		self.pipeline.add (vcomp, acomp, vconv, aconv, vident, aident, vencode, aencode, mux, sink)
		gst.element_link_many (vconv, vident, vencode, mux)
		gst.element_link_many (aconv, aident, aencode, mux)
		gst.element_link_many (mux, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect ("message", self.on_message)

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
			self.pipeline.set_state (gst.STATE_NULL)
			print "EOS"
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state (gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				if 'final' in message.src.get_name():
					self.pipeline.set_state (gst.STATE_NULL)
					self.updatemodel.emit (100, 100)
				elif 'report' in message.src.get_name():
					num = re.findall (r'\d+', message.src.get_name())[0]
					progress = message.structure ['percent']
					self.updatemodel.emit (num, progress)
