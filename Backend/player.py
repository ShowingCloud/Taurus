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
		self.stopped = True
		self.loop = False
		self.startpos = 0
		self.stoppos = 0

		self.player = None

		QtGui.qApp.aboutToQuit.connect (self.quitworker)

	@QtCore.Slot()
	def startworker (self):

		self.player = gst.element_factory_make ("playbin2")
		audiosink = gst.element_factory_make ("autoaudiosink", "audiosink")
		self.player.set_property ("audio-sink", audiosink)
#		videosink = gst.element_factory_make ("dshowvideosink", "videosink")
		videosink = gst.element_factory_make ("autovideosink", "videosink")
		self.player.set_property ("video-sink", videosink)

		self.bus = self.player.get_bus()
		self.bus.enable_sync_message_emission()
		self.bus.add_signal_watch()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.updatelabelduration.emit ("00:00.000 / 00:00.000")
		self.updatesliderseek.emit (self.seekmin)
		self.updateslidervolume.emit (self.volmax)

		self.updatethreadtimer = QtCore.QTimer()
		self.updatethreadtimer.timeout.connect (self.updatethread)
		self.updatethreadtimer.start (10)

		self.player.set_state (gst.STATE_READY)

	@QtCore.Slot (unicode)
	def playuri (self, filepath):

		if self.hasmediafile:
			self.player.set_state (gst.STATE_PAUSED)
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)

		self.startpos = 0
		self.stoppos = 0
		self.loop = False

		self.player.set_state (gst.STATE_NULL)
		self.player.set_property ("uri", "file:///" + filepath)
		self.hasmediafile = True

		self.player.set_state (gst.STATE_PLAYING)
		self.stopped = False
		self.setbuttonpause.emit()
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
			self.dur_str = time2str (self.stoppos - self.startpos)
			self.loop = False
		else:
			self.dur_str = time2str (self.stoppos - self.startpos)
			self.loop = True

		if endtime == 0:
			self.player.set_state (gst.STATE_PAUSED)
			self.setbuttonplay.emit()
		else:
			self.player.set_state (gst.STATE_PLAYING)
			self.setbuttonpause.emit()

	def updatethread (self):
		if self.stoppos == 0:
			try:
				self.duration = self.player.query_duration (gst.FORMAT_TIME, None)[0]
				if not self.duration == -1:
					self.stoppos = self.duration
					self.seek (self.startpos, self.stoppos)
					self.dur_str = time2str (self.stoppos - self.startpos)
					self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
			except:
				pass

		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0]
			self.pos_str = time2str (self.position - self.startpos)
			self.updatelabelduration.emit (self.pos_str + " / " + self.dur_str)
			if self.stoppos != self.startpos:
				self.updatesliderseek.emit (float (self.position - self.startpos) / (self.stoppos - self.startpos)
						* (self.seekmax - self.seekmin) + self.seekmin)
			if not self.stopped:
				self.updatelineedit.emit (self.pos_str)
		except:
			pass

		while True:
			message = self.bus.poll (gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_STATE_CHANGED
					| gst.MESSAGE_SEGMENT_DONE, 0)
			if not message:
				break

			if message.type == gst.MESSAGE_EOS:
				self.stopped = True
				self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
				self.player.set_state (gst.STATE_NULL)
				self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
				self.updatesliderseek.emit (self.seekmin)
				self.setbuttonplay.emit()
			elif message.type == gst.MESSAGE_ERROR:
				self.stopped = True
				self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
				self.player.set_state (gst.STATE_NULL)
				self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
				self.updatesliderseek.emit (self.seekmin)
				err, debug = message.parse_error()
				print 'Error: %s' % err, debug
				self.setbuttonplay.emit()
			elif message.type == gst.MESSAGE_STATE_CHANGED:
				old, new, pending = message.parse_state_changed()
				if old == gst.STATE_READY and new == gst.STATE_PAUSED and message.src == self.player:
					self.seek (self.startpos, self.stoppos)
			elif message.type == gst.MESSAGE_SEGMENT_DONE:
				src = self.player.get_property ("source")
				pad = src.get_pad ('src')
				pad.push_event (gst.event_new_eos())

	def seek (self, start, stop):
		flags = gst.SEEK_FLAG_SEGMENT | gst.SEEK_FLAG_ACCURATE | gst.SEEK_FLAG_FLUSH
		self.player.seek (1.0, gst.FORMAT_TIME, flags, gst.SEEK_TYPE_SET, start, gst.SEEK_TYPE_SET, stop)

	@QtCore.Slot()
	def playclicked (self):
		self.stopped = not self.hasmediafile

		if self.player.get_state (0)[1] == gst.STATE_PLAYING:
			self.player.set_state (gst.STATE_PAUSED)
			self.setbuttonplay.emit()
		else:
			if self.hasmediafile:
				self.player.set_state (gst.STATE_PLAYING)
				self.setbuttonpause.emit()

	@QtCore.Slot()
	def stopclicked (self):
		self.stopped = True

		if self.hasmediafile:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)

		self.player.set_state (gst.STATE_NULL)

		self.setbuttonplay.emit()

		self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
		self.updatesliderseek.emit (self.seekmin)

	@QtCore.Slot()
	def backwardclicked (self):
		if not self.hasmediafile:
			return

		self.stopped = False

		self.player.set_state (gst.STATE_PAUSED)
		self.position -= 100000000

		if self.position < 0:
			self.position = 0

		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	@QtCore.Slot()
	def forwardclicked (self):
		if not self.hasmediafile:
			return

		self.stopped = False

		self.player.set_state (gst.STATE_PAUSED)
		self.position += 100000000

		if self.position > self.stoppos:
			self.position = self.stoppos

		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	@QtCore.Slot()
	def muteornot (self):
		print "got signal"
		if self.player.get_property ("mute") == False:
			self.player.set_property ("mute", True)
			self.updateslidervolume.emit (self.volmin)
		else:
			self.player.set_property ("mute", False)
			self.updateslidervolume.emit (self.player.get_property ("volume") * (self.volmax - self.volmin) + self.volmin)

	@QtCore.Slot (int)
	def sliderseekvalue (self, slider):
		if self.hasmediafile:
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT,
					(float (slider - self.seekmin) / (self.seekmax - self.seekmin)
						* (self.stoppos - self.startpos) + self.startpos))

	@QtCore.Slot (int)
	def slidervolumevalue (self, slider):
		self.player.set_property ("volume", float (slider - self.volmin) / (self.volmax - self.volmin))

	@QtCore.Slot()
	def quitworker (self):
		self.player.set_state (gst.STATE_NULL)

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.stopped = True
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
			self.player.set_state (gst.STATE_NULL)
			self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
			self.updatesliderseek.emit (self.seekmin)
			self.setbuttonplay.emit()
		elif message.type == gst.MESSAGE_ERROR:
			self.stopped = True
			self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.startpos)
			self.player.set_state (gst.STATE_NULL)
			self.updatelabelduration.emit ("00:00.000 / " + self.dur_str)
			self.updatesliderseek.emit (self.seekmin)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.setbuttonplay.emit()
		elif message.type == gst.MESSAGE_STATE_CHANGED:
			old, new, pending = message.parse_state_changed()
			if old == gst.STATE_READY and new == gst.STATE_PAUSED and message.src == self.player:
				self.seek (self.startpos, self.stoppos)
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

	def cb_pad_added (self, element, pad, islast):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked():
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)
