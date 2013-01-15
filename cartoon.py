#!/usr/bin/python

import sys, os, thread, time
import gobject, gst
from PySide import QtCore, QtGui
from ctypes import pythonapi, c_void_p, py_object

import xmlrpclib
import hashlib
from threading import Thread

from ui_mainwindow import Ui_MainWindow
from ui_login import Ui_Login


TransTaskProcessing, TransTaskFinished, TransTaskDeleted = xrange (3)


class MainWindow (QtGui.QMainWindow):

	def __init__ (self, parent = None):
		QtGui.QMainWindow.__init__ (self, parent)

		self.ui = Ui_MainWindow()
		self.ui.setupUi (self)

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.createActions()

		self.transcoding = []
		self.translisting = TransTaskProcessing

		winid = self.ui.frame_2.winId()
		pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
		pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]
		self.windowId = pythonapi.PyCObject_AsVoidPtr (winid)

		self.player = Player (self.ui, self.windowId)
		self.player.start()

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

		self.ui.MovieEdit.clicked.connect (self.changePage1)
		self.ui.FormatConvert.clicked.connect (self.changePage)

		self.ui.tabletrans.setModel (self.transfermodel (self))
		self.ui.tabletrans.setRootIsDecorated (False)
		self.ui.tabletrans.setAlternatingRowColors (True)
		self.ui.tabletrans.setItemDelegate (TransferDelegate (self))
		for i in xrange (4):
			self.ui.tabletrans.setColumnWidth (i, 200)
		self.ui.tabletrans.header().setDefaultAlignment (QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

	def transfermodel (self, parent):
		model = QtGui.QStandardItemModel (0, 4, parent)
		model.setHorizontalHeaderLabels ([self.tr ("Cartoon Name"), self.tr ("Transfer Progress"), self.tr ("Status"), self.tr ("Output Path")])
		return model

#	def resizeEvent (self, event):
#		pixmap = QtGui.QPixmap (self.size())
#		painter = QtGui.QPainter()
#		painter.begin (pixmap)
#		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
#		painter.setBrush (QtCore.Qt.black)
#		painter.drawRoundRect (pixmap.rect(), 5, 5)
#		painter.end()
#
#		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))

	@QtCore.Slot()
	def on_buttonloadfile_clicked (self):

		filepath = QtGui.QFileDialog.getOpenFileName (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		if filepath:
			self.player.playuri (filepath)

	@QtCore.Slot()
	def on_buttonplayerplay_clicked (self):
		self.player.playclicked()

	@QtCore.Slot()
	def on_buttonplayerstop_clicked (self):
		self.player.stopclicked()

	@QtCore.Slot()
	def on_buttonplayerbackward_clicked (self):
		self.player.backwardclicked()

	@QtCore.Slot()
	def on_buttonplayerforward_clicked (self):
		self.player.forwardclicked()

	@QtCore.Slot()
	def on_buttonvolume_clicked (self):
		self.player.muteornot()

	@QtCore.Slot(int)
	def on_sliderseek_valueChanged (self, slider):
		self.player.sliderseekvalue (slider)

	@QtCore.Slot(int)
	def on_slidervolume_valueChanged (self, slider):
		self.player.slidervolumevalue (slider)

	def closeEvent (self, event):
		if self.trayicon.isVisible():
			self.hide()
			event.ignore()

	@QtCore.Slot()
	def on_buttontransnew_clicked (self):

		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		newpath = QtGui.QFileDialog.getExistingDirectory (self, self.tr ("Select output directory"))
		model = self.ui.tabletrans.model()

		while len (files) > 0:
			newfile = QtCore.QFileInfo (files.pop())
			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), newfile.fileName())
			model.setData (model.index (row, 1), 0)
			model.setData (model.index (row, 2), QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, QtCore.Qt.TextAlignmentRole)

			if newpath == "":
				newpath = newfile.absolutePath()
			model.setData (model.index (row, 3), newpath)

			dstfile = newpath + "/" + newfile.baseName() + "-change.mp4"
			transcode = Transcoder (newfile.absoluteFilePath(), dstfile, self, model, row)
			transcode.start()
			self.transcoding.append ({"thread": transcode, "status": TransTaskProcessing})

	@QtCore.Slot()
	def on_buttontransbegin_clicked (self):
		row = self.ui.tabletrans.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["thread"].play()

	@QtCore.Slot()
	def on_buttontranspause_clicked (self):
		row = self.ui.tabletrans.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["thread"].pause()

	@QtCore.Slot()
	def on_buttontransdelete_clicked (self):
		row = self.ui.tabletrans.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["thread"].remove()
			self.transcoding [row] ["status"] = TransTaskDeleted
			self.ui.tabletrans.setRowHidden (row, QtCore.QModelIndex(), True)

	@QtCore.Slot()
	def on_listWidget_itemClicked (self):
		self.translisting = self.ui.listWidget.currentRow()

		for row in xrange (self.ui.tabletrans.model().rowCount()):
			if self.transcoding [row] ["status"] == self.translisting:
				self.ui.tabletrans.setRowHidden (row, QtCore.QModelIndex(), False)
			else:
				self.ui.tabletrans.setRowHidden (row, QtCore.QModelIndex(), True)

	def transfertaskfinished (self, row):
		self.transcoding [row] ["status"] = TransTaskFinished

		if self.translisting == TransTaskProcessing:
			self.ui.tabletrans.setRowHidden (row, QtCore.QModelIndex(), True)
		else:
			self.ui.tabletrans.setRowHidden (row, QtCore.QModelIndex(), False)

	def changePage (self):
#		nextPage = self.ui.stackedWidget.currentIndex() + 1
#		if nextPage >= self.ui.stackedWidget.count():
#			nextPage = 0
		self.ui.stackedWidget.setCurrentIndex (1)

	def changePage1 (self):
#		nextPage = self.ui.stackedWidget.currentIndex() - 1
#		if nextPage >= self.ui.stackedWidget.count():
#			nextPage = 0
		self.ui.stackedWidget.setCurrentIndex (0)


class Player (QtCore.QThread):

	def __init__ (self, ui, windowId, parent = None):

		QtCore.QThread.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.ui = ui
		self.windowId = windowId

	def run (self):

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

		self.ui.lineeditduration.setText("00:00 / 00:00")
		self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())
		self.ui.slidervolume.setValue (self.ui.sliderseek.maximum())

		self.player.set_state (gst.STATE_READY)
		self.mainloop.run()

	def playuri (self, filepath):
		self.player.set_state (gst.STATE_NULL)
		self.player.set_property ("uri", "file:///" + filepath)
		self.player.set_state (gst.STATE_PLAYING)
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/pause.png'))
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

	def playclicked (self):
		if (self.player.get_state (0)[1] == gst.STATE_PLAYING):
			self.player.set_state (gst.STATE_PAUSED)
			self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))
		else:
			self.player.set_state (gst.STATE_PLAYING)
			self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/pause.png'))

	def stopclicked (self):
		self.player.set_state (gst.STATE_NULL)
		self.play_thread_id = None
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))
		self.ui.lineeditduration.setText ("00:00 / 00:00")
		self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())

	def backwardclicked (self):
		self.player.set_state (gst.STATE_PAUSED)
		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0] - 100000000
		except:
			self.position -= 100000000
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	def forwardclicked (self):
		self.player.set_state (gst.STATE_PAUSED)
		try:
			self.position = self.player.query_position (gst.FORMAT_TIME, None)[0] + 100000000
		except:
			self.position += 100000000
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, self.position)

	def muteornot (self):
		if self.player.get_property ("volume") == 0:
			self.player.set_property ("volume", 1)
			self.ui.slidervolume.setValue (self.ui.slidervolume.maximum())
		else:
			self.player.set_property ("volume", 0)
			self.ui.slidervolume.setValue (self.ui.slidervolume.minimum())

	def sliderseekvalue (self, slider):
		self.player.seek_simple (gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, (float (slider - self.ui.sliderseek.minimum()) / (self.ui.sliderseek.maximum() - self.ui.sliderseek.minimum()) * self.duration))

	def slidervolumevalue (self, slider):
		self.player.set_property ("volume", float (slider - self.ui.slidervolume.minimum()) / (self.ui.slidervolume.maximum() - self.ui.slidervolume.minimum()))

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			self.play_thread_id = None
			self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))
			self.ui.lineeditduration.setText ("00:00 / 00:00")
			self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())
		elif message.type == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			self.play_thread_id = None
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))
			self.ui.lineeditduration.setText ("00:00 / 00:00")
			self.ui.sliderseek.setValue (self.ui.sliderseek.minimum())

	def on_sync_message (self, bus, message):
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


class TransferDelegate (QtGui.QStyledItemDelegate):

	def __init__ (self, parent = None):
		QtGui.QStyledItemDelegate.__init__ (self, parent)

	def paint (self, painter, option, index):
		if index.column() == 1:
			style = QtGui.QApplication.style()
			progressbar = QtGui.QStyleOptionProgressBar()
			progressbar.minimum = 0
			progressbar.maximum = 100
			progressbar.textVisible = True
			progressbar.textAlignment = QtCore.Qt.AlignCenter
			progressbar.text = "%d%%" % index.data()
			progressbar.progress = index.data()
			progressbar.rect = option.rect

			style.drawControl (QtGui.QStyle.CE_ProgressBar, progressbar, painter)

		else:
			QtGui.QStyledItemDelegate.paint (self, painter, option, index)

	def createEditor(self, parent, option, index):
		pass


class Login (QtGui.QDialog):

	def __init__ (self, parent = None):
		QtGui.QDialog.__init__ (self, parent)

		self.ui = Ui_Login()
		self.ui.setupUi (self)
		self.ui.lineeditpasswordinput.setEchoMode (QtGui.QLineEdit.Password)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

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
		msg = QtGui.QMessageBox()
		msg.setInformativeText (self.tr ("To contact the administrator for password reset, please dial 0592-XXXXXXXX or send mail to admin@139.com."))
		msg.exec_()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 7, 14)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))


class Transcoder (QtCore.QThread):

	taskfinished = QtCore.Signal (int)

	def __init__ (self, srcfile, dstfile, parent, model, row):

		QtCore.QThread.__init__ (self, parent)
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.srcfile = srcfile
		self.dstfile = dstfile
		self.parent = parent
		self.model = model
		self.row = row

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
		audioenc = gst.element_factory_make ("ffenc_aac")
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
		gst.element_link_many (queuev, videoscale, videorate, colorspace, caps, colorspace2, videoenc, muxer)
		gst.element_link_many (queuea, audioconv, audioenc, muxer)
		gst.element_link_many (muxer, progress, sink)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect ("message", self.on_message)
		self.bus.connect ("sync-message::element", self.on_sync_message)

		self.model.setData (self.model.index (self.row, 1), 0)
		self.model.setData (self.model.index (self.row, 2), self.tr ("Not Started"))

		self.taskfinished.connect (self.parent.transfertaskfinished)

		self.pipeline.set_state (gst.STATE_PAUSED)
		self.mainloop.run()

	def play (self):
		self.pipeline.set_state (gst.STATE_PLAYING)
		self.model.setData (self.model.index (self.row, 2), self.tr ("Transcoding..."))
	
	def pause (self):
		self.pipeline.set_state (gst.STATE_PAUSED)
		self.model.setData (self.model.index (self.row, 2), self.tr ("Paused"))

	def remove (self):
		self.pipeline.set_state (gst.STATE_NULL)
#		self.mainloop.quit()

	def on_message (self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.pipeline.set_state(gst.STATE_NULL)
			self.model.setData (self.model.index (self.row, 1), 100)
			self.model.setData (self.model.index (self.row, 2), self.tr ("Finished"))
			self.taskfinished.emit (self.row)
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print 'Error: %s' % err, debug
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure.get_name() == "progress":
				self.model.setData (self.model.index (self.row, 1), message.structure ['percent'])
				if message.structure ['percent'] >= 100:
					self.model.setData (self.model.index (self.row, 2), self.tr ("Finished"))
					self.taskfinished.emit (self.row)

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
