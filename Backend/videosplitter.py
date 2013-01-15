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
		self.totranscode = False # Not in use
		self.parent = parent

		self.lastprogress = -1
		self.progress = -1

		self.finished.connect (self.quitworker)

		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		if self.dstfileinfo.suffix() == "":
			if not self.totranscode:
				dstfile = "%s.%s" % (dstfile, QtCore.QFileInfo (srcfile).suffix())
			else:
				dstfile = "%s.mp4" % dstfile

		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		dstfile = QtCore.QDir.toNativeSeparators (self.dstfileinfo.absoluteFilePath())
		i = 0
		while os.path.exists (dstfile):
			i += 1
			dstfile = os.path.join (QtCore.QDir.toNativeSeparators (self.dstfileinfo.absolutePath()),
					"%s-%02d.%s" % (self.dstfileinfo.baseName(), i, self.dstfileinfo.suffix()))
		os.close (os.open (dstfile, os.O_CREAT))
		self.dstfileinfo = QtCore.QFileInfo (dstfile)
		self.dstfile = QtCore.QDir.toNativeSeparators (self.dstfileinfo.absoluteFilePath())

		if totranscode:
			self.finished.connect (lambda: self.addtranscode.emit (self.dstfile))

	@QtCore.Slot (unicode)
	def startworker (self, timestring):
		self.dowork()

		self.startnewsplit.emit (timestring, self.dstfileinfo.fileName(),
				QtCore.QDir.toNativeSeparators (self.dstfileinfo.absolutePath()))

	@QtCore.Slot()
	def quitworker (self):
		if self.pipeline:
			self.pipeline.set_state (gst.STATE_NULL)

		self.deleteLater()

	def dowork (self):

		self.pipeline = gst.Pipeline()
		vcomp = gst.element_factory_make ('gnlcomposition')
		vcomp.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))
		acomp = gst.element_factory_make ('gnlcomposition')
		acomp.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))
		vconv = gst.element_factory_make ('ffmpegcolorspace')
		vcomp.connect ("pad-added", self.comp_pad, vconv)
		aconv = gst.element_factory_make ('audioconvert')
		acomp.connect ("pad-added", self.comp_pad, aconv)
		vident = gst.element_factory_make ('identity')
		vident.set_property ('single-segment', True)
#		vident.set_property ('sync', True)
		aident = gst.element_factory_make ('identity')
		aident.set_property ('single-segment', True)
#		aident.set_property ('sync', True)

		if not self.totranscode:
			vencode = gst.element_factory_make (self.params.get ('videoencoder'))
			vencode.set_property ('bitrate', self.params.get ('highestvideobitrate'))
			aencode = gst.element_factory_make (self.params.get ('audioencoder'))
			aencode.set_property ('bitrate', self.params.get ('highestaudiobitrate'))
			mux = gst.element_factory_make (self.params.get ('muxer'))
		else:
			videoscale = gst.element_factory_make ('videoscale')
			videorate = gst.element_factory_make ('videorate')
			videoconv = gst.element_factory_make ('ffmpegcolorspace')
			videocaps = gst.element_factory_make ('capsfilter')
			videocaps.set_property ('caps', gst.caps_from_string ("\
					video/x-raw-yuv, width=640, height=480, framerate=25/1;\
					video/x-raw-rgb, width=640, height=480, framerate=25/1"))
			vencode = gst.element_factory_make ('x264enc')
			vencode.set_property ('bitrate', 1024)
			aencode = gst.element_factory_make ('faac')
			aencode.set_property ('bitrate', 128000)
			mux = gst.element_factory_make ('mp4mux')

		progressreport = gst.element_factory_make ('progressreport', 'output')
		progressreport.set_property ('silent', False)
		progressreport.set_property ('update-freq', 1)
		sink = gst.element_factory_make ('filesink')
		sink.set_property ('location', self.dstfile)

		self.pipeline.add (vcomp, acomp, vconv, aconv, vident, aident, vencode, aencode, mux, progressreport, sink)
		if not self.totranscode:
			gst.element_link_many (vconv, vident, vencode, mux)
		else:
			self.pipeline.add (videoscale, videorate, videoconv, videocaps)
			gst.element_link_many (vconv, vident, videoscale, videorate, videoconv, videocaps, vencode, mux)
		gst.element_link_many (aconv, aident, aencode, mux)
		gst.element_link_many (mux, progressreport, sink)

		timestamp = 0

		if self.title:

			src = gst.Bin()
			source = gst.element_factory_make ('videotestsrc')
			source.set_property ('pattern', 2)
			overlay = gst.element_factory_make ('textoverlay')
			overlay.set_property ('text', self.title)
			overlay.set_property ('font-desc', "Sans Bold 50")
			overlay.set_property ('valignment', 3)
			vconvert = gst.element_factory_make ('ffmpegcolorspace')
			preport = gst.element_factory_make ('progressreport', 'title')
			preport.set_property ('silent', False)
			preport.set_property ('update-freq', 1)
			caps = gst.element_factory_make ('capsfilter')
			caps.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))

			src.add_many (source, overlay, vconvert, preport, caps)
			gst.element_link_many (source, overlay, vconvert, preport, caps)
			src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

			vsrc = gst.element_factory_make ('gnlsource')
			vsrc.set_property ('start', 0)
			vsrc.set_property ('duration', 5 * gst.SECOND)
			vsrc.set_property ('media-start', 0)
			vsrc.set_property ('media-duration', 5 * gst.SECOND)
			vsrc.set_property ('priority', 10)
			vsrc.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))
			vsrc.add (src)
			vcomp.add (vsrc)

			timestamp += 5 * gst.SECOND

		src = gst.Bin()
		source = gst.element_factory_make ('filesrc')
		source.set_property ('location', self.srcfile)
		decode = gst.element_factory_make ('decodebin2')
		decode.set_property ('expose-all-streams', False)
		decode.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))
		vconvert = gst.element_factory_make ('ffmpegcolorspace')
		decode.connect ('pad-added', self.decode_pad, vconvert)
		preport = gst.element_factory_make ('progressreport', 'video')
		preport.set_property ('silent', False)
		preport.set_property ('update-freq', 1)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))

		src.add_many (source, preport, decode, vconvert, caps)
		gst.element_link_many (source, decode)
		gst.element_link_many (vconvert, preport, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', timestamp)
		vsrc.set_property ('duration', self.duration)
		vsrc.set_property ('media-start', self.starttime)
		vsrc.set_property ('media-duration', self.duration)
		vsrc.set_property ('priority', 2)
		vsrc.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))
		vsrc.add (src)
		vcomp.add (vsrc)

		src = gst.Bin()
		source = gst.element_factory_make ('filesrc')
		source.set_property ('location', self.srcfile)
		decode = gst.element_factory_make ('decodebin2')
		decode.set_property ('expose-all-streams', False)
		decode.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))
		aconvert = gst.element_factory_make ('audioconvert')
		decode.connect ('pad-added', self.decode_pad, aconvert)
		preport = gst.element_factory_make ('progressreport', 'audio')
		preport.set_property ('silent', False)
		preport.set_property ('update-freq', 1)
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))

		src.add_many (source, preport, decode, aconvert, caps)
		gst.element_link_many (source, decode)
		gst.element_link_many (aconvert, preport, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', timestamp)
		asrc.set_property ('duration', self.duration)
		asrc.set_property ('media-start', self.starttime)
		asrc.set_property ('media-duration', self.duration)
		asrc.set_property ('priority', 2)
		asrc.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))
		asrc.add (src)
		acomp.add (asrc)

		timestamp += self.duration

		src = gst.Bin()
		source = gst.element_factory_make ('videotestsrc')
		source.set_property ('pattern', 2)
		vconvert = gst.element_factory_make ('ffmpegcolorspace')
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))

		src.add_many (source, vconvert, caps)
		gst.element_link_many (source, vconvert, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		vsrc = gst.element_factory_make ('gnlsource')
		vsrc.set_property ('start', 0)
		vsrc.set_property ('duration', timestamp)
		vsrc.set_property ('media-start', 0)
		vsrc.set_property ('media-duration', timestamp)
		vsrc.set_property ('priority', 100)
		vsrc.set_property ('caps', gst.Caps (self.params.get ('videooutcaps')))
		vsrc.add (src)
		vcomp.add (vsrc)

		src = gst.Bin()
		source = gst.element_factory_make ('audiotestsrc')
		source.set_property ('wave', 4)
		source.set_property ('volume', 0.0)
		source.set_property ('can-activate-pull', True)
		source.set_property ('can-activate-push', True)
		aconvert = gst.element_factory_make ('audioconvert')
		caps = gst.element_factory_make ('capsfilter')
		caps.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))

		src.add_many (source, aconvert, caps)
		gst.element_link_many (source, aconvert, caps)
		src.add_pad (gst.GhostPad ('src', caps.get_pad ('src')))

		asrc = gst.element_factory_make ('gnlsource')
		asrc.set_property ('start', 0)
		asrc.set_property ('duration', timestamp)
		asrc.set_property ('media-start', 0)
		asrc.set_property ('media-duration', timestamp)
		asrc.set_property ('priority', 100)
		asrc.set_property ('caps', gst.Caps (self.params.get ('audiooutcaps')))
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
		self.bus.connect ("message::eos", self.on_message)
		self.bus.connect ("message::error", self.on_message)
		self.bus.connect ("sync-message::element", self.on_message)

		self.updatemodel.emit (0)

		self.pipeline.set_state (gst.STATE_PLAYING)

	def comp_pad (self, comp, pad, nextcomp):
		nextpad = nextcomp.get_compatible_pad (pad, pad.get_caps())
		if nextpad:
			if not nextpad.is_linked():
				pad.link (nextpad)
			else:
				print "Composition pad already linked"
		else:
			print "Composition pad not useful"

	def decode_pad (self, comp, pad, nextcomp):
		nextpad = nextcomp.get_compatible_pad (pad, pad.get_caps())
		if nextpad:
			if not nextpad.is_linked():
				pad.link (nextpad)
			else:
				print "Decode pad already linked"
		else:
			print "Decode pad not useful"

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			print "EOS"
			self.pipeline.set_state (gst.STATE_NULL)
			self.updatemodel.emit (100)
			self.finished.emit()
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state (gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.finished.emit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				try:
					if 'title' in message.src.get_name() or 'output' in message.src.get_name():
						self.progress = message.structure['percent']
						self.updatemodel.emit (self.progress)
					elif 'video' in message.src.get_name() or 'audio' in message.src.get_name():
						self.progress = (message.structure['current'] * gst.SECOND - self.starttime) * 100 / self.duration
						self.updatemodel.emit (self.progress)
				except:
					pass
