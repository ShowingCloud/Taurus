#!/usr/bin/python

import threading, time
import gst
from PySide import QtCore, QtGui

from Toolkit import time2str, str2time


class Player (QtCore.QObject):

	playurisignal = QtCore.Signal (unicode)
	updatelabelduration = QtCore.Signal (unicode)
	updatesliderseek = QtCore.Signal (int)
	updateslidervolume = QtCore.Signal (int)
	updatelineedit = QtCore.Signal (unicode)
	setbuttonplay = QtCore.Signal()
	setbuttonpause = QtCore.Signal()
	setloopsignal = QtCore.Signal (unicode, unicode)
	seekstarttimesignal = QtCore.Signal (unicode)
	playclickedsignal = QtCore.Signal()
	stopclickedsignal = QtCore.Signal()
	backwardclickedsignal = QtCore.Signal()
	forwardclickedsignal = QtCore.Signal()
	muteornotsignal = QtCore.Signal()
	sliderseekvaluesignal = QtCore.Signal (int)
	slidervolumevaluesignal = QtCore.Signal (int)
	quitworkersignal = QtCore.Signal()

	def __init__ (self, windowId, seekmin, seekmax, volmin, volmax, parent = None):

		QtCore.QObject.__init__ (self, parent)

		self.windowId = windowId
		self.seekmin = seekmin
		self.seekmax = seekmax
		self.volmin = volmin
		self.volmax = volmax

		self.position = 0
		self.duration = 0
		self.pos_str = "00:00.000"
		self.dur_str = "00:00.000"

		self.hasmediafile = False
		self.state = gst.STATE_NULL
		self.loop = False
		self.startpos = 0
		self.stoppos = 0
		self.player = None

		self.playurisignal.connect (self.playuri)
		self.setloopsignal.connect (self.setloop)
		self.seekstarttimesignal.connect (self.seekstarttime)
		self.playclickedsignal.connect (self.playclicked)
		self.stopclickedsignal.connect (self.stopclicked)
		self.backwardclickedsignal.connect (self.backwardclicked)
		self.forwardclickedsignal.connect (self.forwardclicked)
		self.muteornotsignal.connect (self.muteornot)
		self.sliderseekvaluesignal.connect (self.sliderseekvalue)
		self.slidervolumevaluesignal.connect (self.slidervolumevalue)

		self.quitworkersignal.connect (self.quitworker)
		self.quitworkersignal.connect (self.deleteLater)
		QtGui.qApp.aboutToQuit.connect (self.quitworker)
		QtGui.qApp.aboutToQuit.connect (self.deleteLater)

	@QtCore.Slot()
	def startworker (self):

		self.player = gst.element_factory_make ("playbin2")
		self.player.set_property ("volume", 1.0)
		audiosink = gst.element_factory_make ("directsoundsink", "audiosink")
		self.player.set_property ("audio-sink", audiosink)
		videosink = gst.element_factory_make ("dshowvideosink", "videosink")
		self.player.set_property ("video-sink", videosink)

		self.bus = self.player.get_bus()
		self.bus.enable_sync_message_emission()
		self.bus.add_signal_watch()
		self.bus.connect ("message::eos", self.on_message)
		self.bus.connect ("message::error", self.on_message)
		self.bus.connect ("message::state-changed", self.on_message)
		self.bus.connect ("message::segment-done", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.updatelabelduration.emit ("00:00.000 / 00:00.000")
		self.updatesliderseek.emit (self.seekmin)
		self.updateslidervolume.emit (self.volmax)

		self.updatethreadtimer = QtCore.QTimer()
		self.updatethreadtimer.timeout.connect (self.updatethread)
		self.updatethreadtimer.start (200)

		self.player.set_state (gst.STATE_READY)

	@QtCore.Slot (unicode)
	def playuri (self, filepath):

		self.startpos = 0
		self.stoppos = 0
		self.position = 0
		self.loop = False

		self.player.set_state (gst.STATE_NULL)
		self.player.set_property ("uri", "file:///%s" % filepath)
		self.hasmediafile = True
		self.player.set_state (gst.STATE_PLAYING)

		self.updatelabelduration.emit ("00:00.000 / 00:00.000")
		self.updatesliderseek.emit (self.seekmin)

	@QtCore.Slot (str, str)
	def setloop (self, start, end):
		starttime = str2time (start)
		endtime = str2time (end)

		if endtime == 0 or starttime >= self.duration:
			self.startpos = 0
			self.stoppos = self.duration
		elif endtime > self.duration:
			self.startpos = starttime
			self.stoppos = self.duration
		else:
			self.startpos = starttime
			self.stoppos = endtime

		self.seek (self.startpos, self.stoppos)

		if endtime == 0:
			self.player.set_state (gst.STATE_PAUSED)
			self.dur_str = time2str (self.stoppos - self.startpos)
			self.loop = False
		else:
			self.player.set_state (gst.STATE_PLAYING)
			self.dur_str = time2str (self.stoppos - self.startpos)
			self.loop = True

	@QtCore.Slot (str)
	def seekstarttime (self, start):
		starttime = str2time (start)

		if self.hasmediafile and starttime <= self.duration:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, starttime)
			self.player.set_state (gst.STATE_PAUSED)

	def updatethread (self):

		if self.stoppos == 0:
			try:
				self.duration = self.player.query_duration (gst.FORMAT_TIME, None)[0]
				if self.duration == -1:
					return
				self.stoppos = self.duration
				self.dur_str = time2str (self.stoppos - self.startpos)
				self.updatelabelduration.emit ("00:00.000 / %s" % self.dur_str)
			except:
				pass

		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0]
			self.pos_str = time2str (self.position - self.startpos)
			self.updatelabelduration.emit ("%s / %s" % (self.pos_str, self.dur_str))
			if self.stoppos != self.startpos:
				self.updatesliderseek.emit ((self.position - self.startpos) * 100 / (self.stoppos - self.startpos))
#						/ 100 * (self.seekmax - self.seekmin) + self.seekmin)
			if self.state == gst.STATE_PLAYING:
				self.updatelineedit.emit (self.pos_str)
		except:
			pass

	def seek (self, start, stop):
		flags = gst.SEEK_FLAG_SEGMENT | gst.SEEK_FLAG_ACCURATE | gst.SEEK_FLAG_FLUSH
		self.player.seek (1.0, gst.FORMAT_TIME, flags, gst.SEEK_TYPE_SET, start, gst.SEEK_TYPE_SET, stop)

	@QtCore.Slot()
	def playclicked (self):
		if not self.hasmediafile:
			return

		if self.state == gst.STATE_PLAYING:
			self.player.set_state (gst.STATE_PAUSED)
		else:
			self.player.set_state (gst.STATE_PLAYING)

	@QtCore.Slot()
	def stopclicked (self):
		self.player.set_state (gst.STATE_READY)

		if self.hasmediafile:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)

		self.updatelabelduration.emit ("00:00.000 / %s" % self.dur_str)
		self.updatesliderseek.emit (self.seekmin)

	@QtCore.Slot()
	def backwardclicked (self):
		if not self.hasmediafile:
			return

		self.player.set_state (gst.STATE_PAUSED)
		self.position -= 0.1 * gst.SECOND
		if self.position < 0:
			self.position = 0

		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	@QtCore.Slot()
	def forwardclicked (self):
		if not self.hasmediafile:
			return

		self.player.set_state (gst.STATE_PAUSED)
		self.position += 0.1 * gst.SECOND
		if self.position > self.stoppos:
			self.position = self.stoppos

		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	@QtCore.Slot()
	def muteornot (self):
		if not self.player.get_property ('mute'):
			self.player.set_property ('mute', True)
			self.updateslidervolume.emit (self.volmin)
		else:
			self.player.set_property ('mute', False)
			self.player.set_property ('volume', 1.0)
#			self.updateslidervolume.emit (self.player.get_property ("volume") * (self.volmax - self.volmin) + self.volmin)
			self.updateslidervolume.emit (self.volmax)

	@QtCore.Slot (int)
	def sliderseekvalue (self, slider):
		if self.hasmediafile:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH,
#					(float (slider - self.seekmin) / (self.seekmax - self.seekmin)
					(slider * (self.stoppos - self.startpos) / 100 + self.startpos))

	@QtCore.Slot (int)
	def slidervolumevalue (self, slider):
		self.player.set_property ("volume", float (slider - self.volmin) / (self.volmax - self.volmin))

	@QtCore.Slot()
	def quitworker (self):
		self.player.set_state (gst.STATE_NULL)

	def on_message (self, bus, message):

		if message.type == gst.MESSAGE_EOS:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
			self.player.set_state (gst.STATE_READY)
			self.updatelabelduration.emit ("00:00.000 / %s" % self.dur_str)
			self.updatesliderseek.emit (self.seekmin)

		elif message.type == gst.MESSAGE_ERROR:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
			self.player.set_state (gst.STATE_READY)
			self.updatelabelduration.emit ("00:00.000 / %s" % self.dur_str)
			self.updatesliderseek.emit (self.seekmin)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug

		elif message.type == gst.MESSAGE_STATE_CHANGED:
			if not message.src == self.player:
				return
			old, new, pending = message.parse_state_changed()
			if self.loop and old == gst.STATE_READY and new == gst.STATE_PAUSED:
				self.seek (self.startpos, self.stoppos)

			self.state = new
			if new == gst.STATE_PLAYING:
				self.updatethreadtimer.setInterval (30)
				self.setbuttonpause.emit()
			else:
				self.updatethreadtimer.setInterval (200)
				self.setbuttonplay.emit()

		elif message.type == gst.MESSAGE_SEGMENT_DONE:
			src = self.player.get_property ("source")
			pad = src.get_pad ('src')
			pad.push_event (gst.event_new_eos())

	def on_sync_message (self, bus, message):
		if message.structure is None:
			return
		message_name = message.structure.get_name()
		if message_name == "prepare-xwindow-id":
			imagesink = message.src
			imagesink.set_property ("force-aspect-ratio", True)
			imagesink.set_xwindow_id (self.windowId)
			imagesink.expose()
