#!/usr/bin/python

import os
import gst
from PySide import QtCore, QtGui

class VideoSplitter (QtCore.QObject):

	updatemodel = QtCore.Signal (int)
	finished = QtCore.Signal()
	startnewsplit = QtCore.Signal (unicode, unicode, unicode)
	addtranscode = QtCore.Signal (unicode)

	def __init__ (self, srcfile, dstfile, starttime, duration, title, totranscode, params, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.srcfile = srcfile
		self.params = params
		self.starttime = starttime
		self.duration = duration
		self.title = title
		self.totranscode = totranscode
		self.parent = parent

		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		if self.dstfileinfo.suffix() == "":
#			dstfile += ".%s" % (QtCore.QFileInfo (srcfile).suffix())
			dstfile += ".mp4"

		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		dstfile = QtCore.QDir.toNativeSeparators (self.dstfileinfo.absoluteFilePath())
		i = 0
		while os.path.exists (dstfile):
			i += 1
#			dstfile = os.path.join (self.dstfileinfo.absolutePath(), self.dstfileinfo.baseName() + "-%02d.%s" % (i, self.dstfileinfo.suffix()))
			dstfile = os.path.join (QtCore.QDir.toNativeSeparators (self.dstfileinfo.absolutePath()), self.dstfileinfo.baseName() + "-%02d.mp4" % i)
		os.close (os.open (dstfile, os.O_CREAT))
		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		self.dstfile = QtCore.QDir.toNativeSeparators (self.dstfileinfo.absoluteFilePath())

	@QtCore.Slot (unicode)
	def startworker (self, timestring):

		self.dowork()

		self.hangchecker = QtCore.QTimer()
		self.hangchecker.timeout.connect (self.hangcheck)
		self.hangchecker.start (3000)

		self.startnewsplit.emit (timestring, self.dstfileinfo.fileName(), QtCore.QDir.toNativeSeparators (self.dstfileinfo.absolutePath()))

	def hangcheck (self):
		if not os.path.exists (self.dstfile) or os.stat (self.dstfile).st_size == 0:
			self.pipeline.set_state (gst.STATE_NULL)
			self.pipeline.set_state (gst.STATE_PLAYING)
		else:
			self.hangchecker.stop()

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
		vencode = gst.element_factory_make (self.params['videoencoder'])
		if self.params['videoencoder'] in ['x264enc']:
			index = 1
		else:
			index = 1000

		if self.params['videobitrate']:
			try:
				vencode.set_property ('bitrate', round (float (self.params['videobitrate']) / 1000) * index)
			except:
				vencode.set_property ('bitrate', 1024 * index)
		else:
			vencode.set_property ('bitrate', 1024 * index)

		aencode = gst.element_factory_make (self.params['audioencoder'])
		if self.params['audioencoder'] in ['lamemp3enc']:
			index = 1
		else:
			index = 1000

		if self.params['audiobitrate']:
			try:
				aencode.set_property ('bitrate', round (float (self.params['audiobitrate']) / 1000) * index)
			except:
				aencode.set_property ('bitrate', 128 * index)
		else:
			aencode.set_property ('bitrate', 128 * index)

		mux = gst.element_factory_make (self.params['muxer'])
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
		gst.element_link_many (vconv, vident, vencode, vqueue, mux)
		gst.element_link_many (aconv, aident, aencode, aqueue, mux)
		gst.element_link_many (mux, preport, sink)

		timestamp = 0

		if self.title:

			src = gst.Bin()
			source = gst.element_factory_make ('videotestsrc')
			source.set_property ('pattern', 2)
			overlay = gst.element_factory_make ('textoverlay')
			overlay.set_property ('text', self.title)
			overlay.set_property ('font-desc', "Sans Bold 50")
			overlay.set_property ('valignment', 3)
			preport = gst.element_factory_make ('progressreport', 'title')
			preport.set_property ('silent', False)
			preport.set_property ('update-freq', 1)
			caps = gst.element_factory_make ('capsfilter')
			caps.set_property ('caps', gst.Caps (self.params['videooutcaps']))

			src.add_many (source, overlay, preport, caps)
			gst.element_link_many (source, overlay, preport, caps)
			src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

			vsrc = gst.element_factory_make ('gnlsource')
			vsrc.set_property ('start', 0)
			vsrc.set_property ('duration', 5 * gst.SECOND)
			vsrc.set_property ('media-start', 0)
			vsrc.set_property ('media-duration', 5 * gst.SECOND)
			vsrc.set_property ('priority', 10)
			vsrc.set_property ('caps', gst.Caps (self.params['videooutcaps']))
			vsrc.set_property ('async-handling', False)
			vsrc.add (src)
			vcomp.add (vsrc)

			timestamp += 5 * gst.SECOND

		src = gst.Bin()
		source = gst.element_factory_make ('filesrc')
		source.set_property ('location', self.srcfile)
		decode = gst.element_factory_make ('decodebin2')
		vconvert = gst.element_factory_make ('ffmpegcolorspace')
		preport = gst.element_factory_make ('progressreport', 'video')
		preport.set_property ('silent', False)
		preport.set_property ('update-freq', 1)
		fakesink = gst.element_factory_make ('fakesink')
		decode.connect ('pad-added', self.decode_pad, vconvert, fakesink)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params['videooutcaps']))

		src.add_many (source, preport, decode, vconvert, caps, fakesink)
		gst.element_link_many (source, decode)
		gst.element_link_many (vconvert, preport, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', timestamp)
		vsrc.set_property ('duration', self.duration)
		vsrc.set_property ('media-start', self.starttime)
		vsrc.set_property ('media-duration', self.duration)
		vsrc.set_property ('priority', 2)
		vsrc.set_property ('caps', gst.Caps (self.params['videooutcaps']))
		vsrc.set_property ('async-handling', False)
		vsrc.add (src)
		vcomp.add (vsrc)

		src = gst.Bin()
		source = gst.element_factory_make ('filesrc')
		source.set_property ('location', self.srcfile)
		preport.set_property ('update-freq', 1)
		decode = gst.element_factory_make ('decodebin2')
		aconvert = gst.element_factory_make ('audioconvert')
		preport = gst.element_factory_make ('progressreport', 'audio')
		preport.set_property ('silent', False)
		fakesink = gst.element_factory_make ('fakesink')
		decode.connect ('pad-added', self.decode_pad, aconvert, fakesink)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params['audiooutcaps']))

		src.add_many (source, preport, decode, aconvert, caps, fakesink)
		gst.element_link_many (source, decode)
		gst.element_link_many (aconvert, preport, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', timestamp)
		asrc.set_property ('duration', self.duration)
		asrc.set_property ('media-start', self.starttime)
		asrc.set_property ('media-duration', self.duration)
		asrc.set_property ('priority', 2)
		asrc.set_property ('caps', gst.Caps (self.params['audiooutcaps']))
		asrc.set_property ('async-handling', False)
		asrc.add (src)
		acomp.add (asrc)

		timestamp += self.duration

		src = gst.Bin()
		source = gst.element_factory_make ('videotestsrc')
		source.set_property ('pattern', 2)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params['videooutcaps']))

		src.add_many (source, caps)
		gst.element_link_many (source, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', 0)
		vsrc.set_property ('duration', timestamp)
		vsrc.set_property ('media-start', 0)
		vsrc.set_property ('media-duration', timestamp)
		vsrc.set_property ('priority', 1000)
		vsrc.set_property ('caps', gst.Caps (self.params['videooutcaps']))
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
		caps.set_property ('caps', gst.Caps (self.params['audiooutcaps']))

		src.add_many (source, caps)
		gst.element_link_many (source, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', 0)
		asrc.set_property ('duration', timestamp)
		asrc.set_property ('media-start', 0)
		asrc.set_property ('media-duration', timestamp)
		asrc.set_property ('priority', 1000)
		asrc.set_property ('caps', gst.Caps (self.params['audiooutcaps']))
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

		self.updatemodel.emit (0)

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
			try:
				self.updatemodel.emit (100)
				self.finished.emit()
			except:
				pass
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state (gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.finished.emit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				if 'output' in message.src.get_name() or 'video' in message.src.get_name() or 'audio' in message.src.get_name():
					try:
						self.updatemodel.emit (message.structure ['percent'])
					except:
						pass
