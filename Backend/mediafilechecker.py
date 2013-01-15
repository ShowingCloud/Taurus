#!/usr/bin/python

import os
import gst
from PySide import QtCore, QtGui


class MediaFileChecker (QtCore.QObject):

	discoveredsignal = QtCore.Signal (int, bool, dict)
	finished = QtCore.Signal()

	def __init__ (self, mediafile, row, parent = None):
		QtCore.QObject.__init__ (self, parent)

		self.mediafile = mediafile
		self.row = row

		self.demuxer = None
		self.muxer = None
		self.status = 0
		self.length = -1

		self.gotaout = False
		self.gotvout = False
		self.gotacodec = False
		self.gotvcodec = False

		self.vcodeccaps = None
		self.acodeccaps = None
		self.voutcaps = None
		self.aoutcaps = None

		self.vwidth = None
		self.vheight = None
		self.vbitrate = None
		self.abitrate = None
		self.vframerate = None

	@QtCore.Slot()
	def startworker (self):

		if not os.path.isfile (self.mediafile):
			self.discoveredsignal.emit (self.row, False, {})
			self.finished.emit()
			return

		self.contexttimer = QtCore.QTimer()
		self.contexttimer.timeout.connect (self.on_timeout)
		self.contexttimer.start (100)

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.mediafile)
		typefind = gst.element_factory_make ("typefind")
		typefind.connect ("have-type", self.got_encaps_type)
		fakesink = gst.element_factory_make ("fakesink")

		self.pipeline.add (source, typefind, fakesink)
		gst.element_link_many (source, typefind, fakesink)

		self.bus = self.pipeline.get_bus()

		self.pipeline.set_state (gst.STATE_PLAYING)

	def on_timeout (self):

		while True:
			message = self.bus.poll (gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_TAG, 0)
			if not message:
				break

			if message.type == gst.MESSAGE_EOS:
				self.pipeline.set_state (gst.STATE_NULL)

				if self.status == 0:
					self.status =1
				elif self.status == 2:
					self.status = 3
				elif self.status == 4:
					self.status = 5

			elif message.type == gst.MESSAGE_ERROR:
				self.pipeline.set_state (gst.STATE_NULL)

				if self.status == 0:
					self.status =1
				elif self.status == 2:
					self.status = 3
				elif self.status == 4:
					self.status = 5

			elif message.type == gst.MESSAGE_TAG:
				taglist = message.parse_tag()

				if "bitrate" in taglist.keys():
					if "video-codec" in taglist.keys():
						self.vbitrate = taglist["bitrate"]
					elif "audio-codec" in taglist.keys():
						self.abitrate = taglist["bitrate"]
					elif "video" in message.src.get_name():
						self.vbitrate = taglist["bitrate"]
					elif "audio" in message.src.get_name():
						self.abitrate = taglist["bitrate"]

		if self.status == 1:
			self.status = 2
			self.pipeline.set_state (gst.STATE_NULL)
			self.continueworker()
			return

		elif self.status == 3:
			if not self.gotacodec or not self.gotvcodec:
				self.status = 1
				return
			self.status = 4
			self.pipeline.set_state (gst.STATE_NULL)
			self.finishworker()
			return

		elif self.status == 5:
			if not self.gotaout or not self.gotvout:
				self.status = 3
				return
			self.status = 6
			self.pipeline.set_state (gst.STATE_NULL)
			self.discoveredsignal.emit (self.row, self.mediafileverification(), {"muxer": self.muxer, "videocodeccaps": self.vcodeccaps,
				"length": self.length, "audiocodeccaps": self.acodeccaps, "videooutcaps": self.voutcaps, "audiooutcaps": self.aoutcaps,
				"videowidth": self.vwidth, "videoheight": self.vheight, "videobitrate": self.vbitrate, "audiobitrate": self.abitrate,
				"videoframerate": self.vframerate})
			self.finished.emit()

	def mediafileverification (self):
		if not self.muxer:
			return False
		if not self.vcodeccaps or not self.acodeccaps or not self.voutcaps or not self.aoutcaps:
			return False
		if not self.vwidth or not self.vheight:
			return False
		if self.vwidth < 640 or self.vheight < 480:
			return False
		if not self.length or self.length <= 0:
			return False
		if self.vframerate and self.vframerate < 25:
			return False
		if self.vbitrate and self.vbitrate < 4000000:
			return False
		if self.abitrate and self.abitrate < 128000:
			return False

		self.status = 1

		return True

	def got_encaps_type (self, element, probability, caps):
		name = caps[0].get_name()

		if name == "video/mpeg" or name == "video/x-mpeg":
			self.demuxer = "mpegpsdemux"
			self.muxer = "mpegpsmux"
		elif name == "video/x-msvideo":
			self.demuxer = "avidemux"
			self.muxer = "avimux"
		elif name == "video/x-ms-asf":
			self.demuxer = "asfdemux"
			self.muxer = "asfmux"
		elif name == "video/quicktime":
			self.demuxer = "qtdemux"
			self.muxer = "qtmux"
		else:
			return

	def continueworker (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.mediafile)
		demux = gst.element_factory_make (self.demuxer)
		demux.connect ("pad-added", self.new_pad)
		queuea = gst.element_factory_make ("queue")
		queuev = gst.element_factory_make ("queue")
		typefinda = gst.element_factory_make ("typefind")
		typefinda.connect ("have-type", self.got_acodec_type)
		typefindv = gst.element_factory_make ("typefind")
		typefindv.connect ("have-type", self.got_vcodec_type)
		fakesinka = gst.element_factory_make ("fakesink")
		fakesinkv = gst.element_factory_make ("fakesink")

		self.__apad = queuea.get_pad ("sink")
		self.__vpad = queuev.get_pad ("sink")

		self.pipeline.add (source, demux, queuev, queuea, typefindv, typefinda, fakesinkv, fakesinka)
		gst.element_link_many (source, demux)
		gst.element_link_many (queuev, typefindv, fakesinkv)
		gst.element_link_many (queuea, typefinda, fakesinka)

		self.bus = self.pipeline.get_bus()

		self.pipeline.set_state (gst.STATE_PLAYING)

	def got_acodec_type (self, element, probability, caps):
		self.acodeccaps = caps.copy()
		if caps[0].has_key ("bitrate"):
			self.abitrate = caps[0]["bitrate"]
		self.gotacodec = True

		if self.gotvcodec:
			self.status = 3

	def got_vcodec_type (self, element, probability, caps):
		self.vcodeccaps = caps.copy()
		if caps[0].has_key ("bitrate"):
			self.vbitrate = caps[0]["bitrate"]
		self.gotvcodec = True

		if self.gotacodec:
			self.status = 3

	def finishworker (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.mediafile)
		decode = gst.element_factory_make ("decodebin2")
		decode.connect ("pad-added", self.new_pad)
		queuev = gst.element_factory_make ("queue")
		queuea = gst.element_factory_make ("queue")
		typefindv = gst.element_factory_make ("typefind")
		typefindv.connect ("have-type", self.got_vout_type)
		typefinda = gst.element_factory_make ("typefind")
		typefinda.connect ("have-type", self.got_aout_type)
		fakesinkv = gst.element_factory_make ("fakesink")
		fakesinka = gst.element_factory_make ("fakesink")

		self.__vpad = queuev.get_pad ("sink")
		self.__apad = queuea.get_pad ("sink")

		self.pipeline.add (source, decode, queuev, queuea, typefindv, typefinda, fakesinkv, fakesinka)
		gst.element_link_many (source, decode)
		gst.element_link_many (queuev, typefindv, fakesinkv)
		gst.element_link_many (queuea, typefinda, fakesinka)

		self.bus = self.pipeline.get_bus()

		self.pipeline.set_state (gst.STATE_PLAYING)

	def got_aout_type (self, element, probability, caps):
		self.aoutcaps = caps.copy()

		if self.length < 0:
			self.length = self.pipeline.query_duration (gst.FORMAT_TIME, None)[0]
		self.gotaout = True

		if self.gotvout:
			self.status = 5

	def got_vout_type (self, element, probability, caps):
		self.voutcaps = caps.copy()
		self.vheight = caps[0]["height"]
		self.vwidth = caps[0]["width"]
		self.vframerate = caps[0]["framerate"].num / caps[0]["framerate"].denom

		if self.length < 0:
			self.length = self.pipeline.query_duration (gst.FORMAT_TIME, None)[0]
		self.gotvout = True

		if self.gotaout:
			self.status = 5

	def new_pad (self, element, pad):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked():
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)
