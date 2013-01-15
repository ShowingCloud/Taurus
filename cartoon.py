#!/usr/bin/python

import sys, os, thread, time, shutil
import gobject, gst
from PySide import QtCore, QtGui
from ctypes import pythonapi, c_void_p, py_object

import xmlrpclib
import hashlib
from threading import Thread

from ui_mainwindow import Ui_MainWindow
from ui_login import Ui_Login


class MainWindow (QtGui.QMainWindow):

	def __init__ (self, parent = None):
		QtGui.QMainWindow.__init__ (self, parent)

		self.ui = Ui_MainWindow()
		self.ui.setupUi (self)

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.createActions()

		self.transcoding = []

		winid = self.ui.frame_2.winId()
		pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
		pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]
		self.windowId = pythonapi.PyCObject_AsVoidPtr (winid)

	def createActions (self):
		self.restact = QtGui.QAction (self.tr ("&Restore"), self, triggered = self.showNormal)
		self.minact = QtGui.QAction (self.tr ("Mi&nimize"), self, triggered = self.showMinimized)
		self.maxact = QtGui.QAction (self.tr ("Ma&ximize"), self, triggered = self.showMaximized)
		self.quitact = QtGui.QAction (self.tr ("&Quit"), self, triggered = sys.exit)

		self.trayicon = QtGui.QSystemTrayIcon (QtGui.QIcon (':/images/icon.png'))

		self.trayiconmenu = QtGui.QMenu (self)
		self.trayiconmenu.addAction (self.minact)
		self.trayiconmenu.addAction (self.maxact)
		self.trayiconmenu.addAction (self.restact)
		self.trayiconmenu.addSeparator()
		self.trayiconmenu.addAction (self.quitact)

		self.trayicon.setToolTip (self.tr ("Minimize to system tray. Right click this icon and choose Quit to close."))
		self.trayicon.setContextMenu (self.trayiconmenu)

		self.trayicon.show()
		self.trayicon.showMessage (self.tr ("Cartoon Encoding and Uploading Platform"), self.tr ("Minimize to system tray. Right click this icon and choose Quit to close."), QtGui.QSystemTrayIcon.Information, 10000)

		self.player = gst.element_factory_make ("playbin2")
		audiosink = gst.element_factory_make ("autoaudiosink", "audiosink")
		self.player.set_property ("audio-sink", audiosink)
		videosink = gst.element_factory_make ("dshowvideosink", "videosink")
#		videosink = gst.element_factory_make ("autovideosink", "videosink")
		self.player.set_property ("video-sink", videosink)

		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)
		self.player.set_state (gst.STATE_NULL)

		self.ui.MovieEdit.clicked.connect (self.changePage1)
		self.ui.FormatConvert.clicked.connect (self.changePage)

		self.ui.lineeditduration.setText("00:00 / 00:00")
		self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())
		self.ui.slidervolume.setValue (self.ui.sliderseek.maximum())

	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			self.play_thread_id = None
			self.ui.lineeditduration.setText ("00:00 / 00:00")
			self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())
		elif message.type == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			self.play_thread_id = None
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.ui.lineeditduration.setText ("00:00 / 00:00")
			self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())

	def on_sync_message(self, bus, message):
		if message.structure is None:
			return
		message_name = message.structure.get_name()
		if message_name == "prepare-xwindow-id":
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			imagesink.set_xwindow_id (self.windowId)

	def cb_pad_added (self, element, pad, islast):
		caps = pad.get_caps()
		name = caps[0].get_name()
		if 'audio' in name:
			if not self.__apad.is_linked(): # Only link once
				pad.link (self.__apad)
		elif 'video' in name:
			if not self.__vpad.is_linked():
				pad.link (self.__vpad)

	@QtCore.Slot()
	def on_buttonloadfile_clicked (self):

		filepath = QtGui.QFileDialog.getOpenFileName (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		if filepath:
			self.player.set_state (gst.STATE_NULL)
			self.player.set_property ("uri", "file:///" + filepath)
			self.player.set_state (gst.STATE_PLAYING)
			self.play_thread_mutex = QtCore.QMutex()
			self.play_thread_id = thread.start_new_thread (self.play_thread, (self.play_thread_mutex,))

	def play_thread (self, mutex):
		play_thread_id = self.play_thread_id
		mutex.lock()
		self.ui.lineeditduration.setText ("00:00 / 00:00")
		self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())
		mutex.unlock()

		while play_thread_id == self.play_thread_id:
			time.sleep (0.2)
			try:
				self.duration = self.player.query_duration (gst.FORMAT_TIME, None)[0]
				if self.duration == -1:
					continue
				dur_str = self.convert_ns (self.duration)
				mutex.lock()
				self.ui.lineeditduration.setText ("00:00 / " + dur_str)
				mutex.unlock()
				break
			except:
				pass

		time.sleep (0.2)
		while play_thread_id == self.play_thread_id:
			try:
				self.position = self.player.query_position (gst.FORMAT_TIME, None)[0]
				pos_str = self.convert_ns (self.position)
				if play_thread_id == self.play_thread_id:
					mutex.lock()
					self.ui.lineeditduration.setText (pos_str + " / " + dur_str)
					self.ui.sliderseek.blockSignals (True)
					self.ui.sliderseek.setValue (float (self.position) / self.duration * (self.ui.sliderseek.maximum() - self.ui.sliderseek.minimum()) + self.ui.sliderseek.minimum())
					self.ui.sliderseek.blockSignals (False)
					mutex.unlock()
			except:
				pass
			time.sleep (1)

	def convert_ns (self, t):
		# This method was submitted by Sam Mason.
		# It's much shorter than the original one.
		s,ns = divmod (t, 1000000000)
		m,s = divmod (s, 60)

		if m < 60:
			return "%02i:%02i" % (m,s)
		else:
			h,m = divmod (m, 60)
			return "%i:%02i:%02i" % (h,m,s)

	@QtCore.Slot()
	def on_buttonplayerplay_clicked (self):
		if (self.player.get_state (0)[1] == gst.STATE_PLAYING):
			self.player.set_state (gst.STATE_PAUSED)
		else:
			self.player.set_state (gst.STATE_PLAYING)

	@QtCore.Slot()
	def on_buttonplayerstop_clicked (self):
		self.player.set_state (gst.STATE_NULL)
		self.play_thread_id = None
		self.ui.lineeditduration.setText ("00:00 / 00:00")
		self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())

	@QtCore.Slot()
	def on_buttonplayerbackward_clicked (self):
		self.player.set_state (gst.STATE_PAUSED)
		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0] - 100000000
		except:
			self.position -= 100000000
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	@QtCore.Slot()
	def on_buttonplayerforward_clicked (self):
		self.player.set_state (gst.STATE_PAUSED)
		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0] + 100000000
		except:
			self.position += 100000000
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	def on_sliderseek_valueChanged (self, slider):
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, (float (slider - self.ui.sliderseek.minimum()) / (self.ui.sliderseek.maximum() - self.ui.sliderseek.minimum()) * self.duration))

	def on_slidervolume_valueChanged (self, slider):
		self.player.set_property ("volume", float (slider - self.ui.slidervolume.minimum()) / (self.ui.slidervolume.maximum() - self.ui.slidervolume.minimum()))

	def closeEvent (self, event):
		if self.trayicon.isVisible():
			self.hide()
			event.ignore()

	@QtCore.Slot()
	def on_buttontransnew_clicked (self):

		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		tab = self.ui.tabletrans

		while len (files) > 0:
			newfile = QtCore.QFileInfo (files.pop())
			tab.insertRow (tab.rowCount())

			newitem = QtGui.QTableWidgetItem (newfile.fileName())
			tab.setItem (tab.rowCount() - 1, 0, newitem)

			newitem = QtGui.QProgressBar()
			newitem.setRange (0, 100)
			newitem.setTextVisible (True)
			newitem.setAlignment (QtCore.Qt.AlignCenter)
			newitem.setValue (0)
			tab.setCellWidget (tab.rowCount() - 1, 1, newitem)

			newitem = QtGui.QTableWidgetItem (self.tr ("Transcoding..."))
			tab.setItem (tab.rowCount() - 1, 2, newitem)

			newitem = QtGui.QTableWidgetItem (newfile.absolutePath())
			tab.setItem (tab.rowCount() - 1, 3, newitem)

			dstfile = newfile.absolutePath() + "/" + hashlib.md5 (newfile.fileName()).hexdigest() + ".mp4"
			transcode = Transcoder (newfile.absoluteFilePath(), dstfile, self, tab.rowCount() - 1)
			transcode.start()
			self.transcoding.append (transcode)

	def updatetable (self, rownum, newvalue):
		item = self.ui.tabletrans.cellWidget (rownum, 1)
		if item:
			item.setValue (newvalue)

		if newvalue >= 100:
			item = self.ui.tabletrans.item (rownum, 2)
			if item:
				item.setText (self.tr ("Finished"))

	def changePage (self):
		nextPage = self.ui.stackedWidget.currentIndex() + 1
		if nextPage >= self.ui.stackedWidget.count():
			nextPage = 0
		self.ui.stackedWidget.setCurrentIndex (nextPage)

	def changePage1 (self):
		nextPage = self.ui.stackedWidget.currentIndex() - 1
		if nextPage >= self.ui.stackedWidget.count():
			nextPage = 0
		self.ui.stackedWidget.setCurrentIndex (nextPage)


class Login (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_Login()
		self.ui.setupUi (self)
		self.ui.lineeditpasswordinput.setEchoMode (QtGui.QLineEdit.Password)
#		self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True);
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

#		self.ui.centralWidget.setStyleSheet("\
#				border-top-left-radius: 15px;\
#				border-bottom-left-radius: 15px;\
#				border-bottom-right-radius: 15px;\
#				border-top-right-radius: 15px;");

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform: Login"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		self.close()

	@QtCore.Slot()
	def on_buttonaccept_clicked (self):
		s = xmlrpclib.ServerProxy ("http://61.147.79.115:10207")

#		if s.CheckLogin (self.ui.lineeditcpidinput.text().trimmed().toLatin1().data(), self.ui.lineeditpasswordinput.text().trimmed().toLatin1().data()):
		if s.CheckLogin (self.ui.lineeditcpidinput.text(), self.ui.lineeditpasswordinput.text()):
			self.accept()
		else:
			mbox = QtGui.QMessageBox()
			mbox.setText (self.tr ("Login error. Exiting."))
			mbox.exec_()
			self.reject()

	@QtCore.Slot()
	def on_buttonforgetpassword_clicked (self):
		pass


class Transcoder (QtCore.QThread):

	updatetriggered = QtCore.Signal(int, int)

	def __init__ (self, srcfile, dstfile, parent, rownum):

		QtCore.QThread.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.srcfile = srcfile
		self.dstfile = dstfile
		self.parent = parent
		self.rownum = rownum

	def run (self):

		self.pipeline = gst.Pipeline ("pipeline")
		source = gst.element_factory_make ("filesrc")
		source.set_property ("location", self.srcfile)
		decoder = gst.element_factory_make ("decodebin2")
		decoder.connect ("new-decoded-pad", self.cb_pad_added)
		queuea = gst.element_factory_make ("queue")
		queuev = gst.element_factory_make ("queue")
		videoscale = gst.element_factory_make ("videoscale")
		videorate = gst.element_factory_make ("videorate")
		audioconv = gst.element_factory_make ("audioconvert")
		colorspace = gst.element_factory_make ("ffmpegcolorspace")
		colorspace2 = gst.element_factory_make ("ffmpegcolorspace")
		caps = gst.element_factory_make ("capsfilter")
		caps.set_property ('caps', gst.caps_from_string ("video/x-raw-rgb, width=640, height=480, framerate=25/1"))
		audioenc = gst.element_factory_make ("faac")
		audioenc.set_property ('bitrate', 128000)
		videoenc = gst.element_factory_make ("x264enc")
		videoenc.set_property ('bitrate', 1024)
		muxer = gst.element_factory_make ("mp4mux")
		sink = gst.element_factory_make ("filesink")
		sink.set_property ("location", self.dstfile)
		progress = gst.element_factory_make ("progressreport")
		progress.set_property ('silent', True)
		progress.set_property ('update-freq', 1)

		self.__apad = queuea.get_pad ("sink")
		self.__vpad = queuev.get_pad ("sink")

		self.pipeline.add (source, decoder, queuea, queuev, audioenc, videoenc, muxer, progress, sink, colorspace, caps, videoscale, videorate, audioconv, colorspace2)
		gst.element_link_many (source, decoder)
		gst.element_link_many (queuev, colorspace, videoscale, videorate, caps, colorspace2, videoenc, muxer)
		gst.element_link_many (queuea, audioconv, audioenc, muxer)
		gst.element_link_many (muxer, progress, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.updatetriggered.connect (self.parent.updatetable)

		self.pipeline.set_state (gst.STATE_PLAYING)
		self.mainloop.run()
		self.pipeline.set_state (gst.STATE_NULL)

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
			if message.structure.get_name() == "progress":
				self.updatetriggered.emit (self.rownum, message.structure ['percent'])

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


if __name__ == "__main__":

	app = QtGui.QApplication (sys.argv)
	QtGui.QApplication.setQuitOnLastWindowClosed (False)

	locale = QtCore.QLocale.system().name()
	appTranslator = QtCore.QTranslator()
	if appTranslator.load ("cartoon_" + locale):
		app.installTranslator (appTranslator)

	l = Login()

	if l.exec_() == QtGui.QDialog.Accepted:
		w = MainWindow()
		#w.identity = login.identity
		w.show()
		sys.exit (app.exec_())
	else:
		sys.exit()
