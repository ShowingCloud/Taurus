#!/usr/bin/python

import sys, os, time, shutil
from PySide import QtCore, QtGui
from ctypes import pythonapi, c_void_p, py_object

from UI import Ui_MainWindow
from Frontend import MergeExam
from Backend import Player, VideoSplitter, VideoMerger, MediaFileChecker, Transcoder
from Toolkit import TransferDelegate, MergeDelegate, time2str, str2time

TransTaskProcessing, TransTaskFinished, TransTaskDeleted = xrange (3)
MergeTaskProcessing, MergeTaskFinished, MergeTaskDeleted = xrange (3)
SplitNotChosen, SplitAdjustStart, SplitAdjustStop = xrange (3)


class MainWindow (QtGui.QMainWindow):

	def __init__ (self, username, edited, transfered, lastsplittime, lastsplitfile, lastsplitpath,
			lastmergepath, lasttransferpath, parent = None):
		QtGui.QMainWindow.__init__ (self, parent)

		self.edited = edited
		self.transfered = transfered
		self.lastsplittime = lastsplittime
		self.lastsplitfile = lastsplitfile
		self.lastsplitpath = lastsplitpath
		self.lastmergepath = lastmergepath
		self.lasttransferpath = lasttransferpath

		self.ui = Ui_MainWindow()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint)

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.createActions()
		self.createplayer()
		self.createmerger()
		self.createUIdetails()

		self.transcoding = []
		self.translisting = TransTaskProcessing
		self.checkers = []
		self.splitchoose = SplitNotChosen
		self.updatelineeditblocked = False

		self.leftclicked = False

		tmppath = os.path.join (os.getcwd(), "tmp")
		if os.path.exists (tmppath):
			shutil.rmtree (tmppath)
		os.makedirs (tmppath)

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

		self.trayiconmenu.setStyleSheet ("QMenu {background-color: rgba(255, 255, 255, 255); border: 1px solid black;} QMenu::item {background-color: transparent;} QMenu::item:selected {background-color: rgba(0, 100, 255, 128);}")

		self.trayicon.setToolTip (self.tr ("Minimize to system tray. Right click this icon and choose Quit to close."))
		self.trayicon.setContextMenu (self.trayiconmenu)

		self.trayicon.show()

		self.trayicon.activated.connect (self.trayiconactivated)

	def createUIdetails (self):

		self.ui.transview.setModel (self.transfermodel (self))
		self.ui.transview.setRootIsDecorated (False)
		self.ui.transview.setAlternatingRowColors (True)
		self.ui.transview.setItemDelegate (TransferDelegate (self))
		for i in xrange (4):
			self.ui.transview.setColumnWidth (i, 170)
		self.ui.transview.header().setDefaultAlignment (QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

		self.ui.mergeview.setModel (self.mergemodel (self))
		self.ui.mergeview.setRootIsDecorated (False)
		self.ui.mergeview.setAlternatingRowColors (True)
		self.ui.mergeview.setItemDelegate (MergeDelegate (self))
		for i in xrange (4):
			self.ui.mergeview.setColumnWidth (i, 200)
		self.ui.mergeview.header().setDefaultAlignment (QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

		self.ui.stackedWidget.setCurrentIndex (0)

		self.ui.lineeditstarttime.installEventFilter (self)
		self.ui.lineeditendtime.installEventFilter (self)

		self.ui.labelvideoedit.setText (self.tr ("Video Edit: %d") % (self.edited))
		self.ui.labelvideoconvert.setText (self.tr ("Video Transfer: %d") % (self.transfered))
		if self.lastsplittime is not None:
			self.ui.labellastrecordtime.setText (self.lastsplittime)
		if self.lastsplitfile is not None:
			self.ui.labellastsavefile.setText (self.lastsplitfile)
		if self.lastmergepath is not None:
			self.ui.lineeditsaveblank.setText (self.lastmergepath)

		self.ui.buttoncancelbrowse.hide()

		self.ui.labelduration.setAlignment (QtCore.Qt.AlignHCenter)

	@QtCore.Slot (int)
	def trayiconactivated (self, event):
		if event == QtGui.QSystemTrayIcon.Trigger:
			if self.isHidden():
				self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/maximize.png'))
				self.showNormal()
			else:
				self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/maximize.png'))
				self.hide()

	@QtCore.Slot()
	def on_buttonminimize_clicked (self):
		self.showMinimized()

	@QtCore.Slot()
	def on_buttonmaximize_clicked (self):
		if (self.isMaximized()):
			self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/maximize.png'))
			self.showNormal()
		else:
			self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/restore.png'))
			self.showMaximized()

	@QtCore.Slot()
	def on_buttonclose_clicked (self):
		self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/maximize.png'))
		self.hide()
		self.trayicon.showMessage (self.tr ("Cartoon Encoding and Uploading Platform"),
				self.tr ("Minimize to system tray. Right click this icon and choose Quit to close."),
				QtGui.QSystemTrayIcon.Information, 10000)

	def transfermodel (self, parent):
		model = QtGui.QStandardItemModel (0, 4, parent)
		model.setHorizontalHeaderLabels ([self.tr ("Cartoon Name"), self.tr ("Transfer Progress"), self.tr ("Status"), self.tr ("Output Path")])
		return model

	def mergemodel (self, parent):
		model = QtGui.QStandardItemModel (0, 4, parent)
		model.setHorizontalHeaderLabels ([self.tr ("File Name"), self.tr ("Duration"), self.tr ("Resolution"), self.tr ("Status")])
		return model

	def createplayer (self):

		winid = self.ui.frame_2.winId()
		pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
		pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]
		self.windowId = pythonapi.PyCObject_AsVoidPtr (winid)

		self.ui.frame_2.mouseMoveEvent = self.mouseMoveEvent
		self.ui.frame_2.mousePressEvent = self.mousePressEvent
		self.ui.frame_2.mouseReleaseEvent = self.frameMouseRelease

		self.playerworker = Player (self.windowId, self.ui.sliderseek.minimum(), self.ui.sliderseek.maximum(), self.ui.slidervolume.minimum(), self.ui.slidervolume.maximum())
#		self.player = QtCore.QThread()
#		self.playerworker.moveToThread (self.player)

		self.ui.buttonplayerplay.clicked.connect (self.playerworker.playclicked)
		self.ui.buttonplayerstop.clicked.connect (self.playerworker.stopclicked)
		self.ui.buttonplayerbackward.clicked.connect (self.playerworker.backwardclicked)
		self.ui.buttonplayerforward.clicked.connect (self.playerworker.forwardclicked)
		self.ui.buttonvolume.clicked.connect (self.playerworker.muteornot)
		self.ui.sliderseek.valueChanged.connect (self.playerworker.sliderseekvalue)
		self.ui.slidervolume.valueChanged.connect (self.playerworker.slidervolumevalue)

		self.playerworker.playurisignal.connect (self.playerworker.playuri)
		self.playerworker.updatelabelduration.connect (self.updatelabelduration)
		self.playerworker.updatesliderseek.connect (self.updatesliderseek)
		self.playerworker.updateslidervolume.connect (self.updateslidervolume)
		self.playerworker.updatelineedit.connect (self.updatelineedit)
		self.playerworker.setbuttonplay.connect (self.playersetbuttonplay)
		self.playerworker.setbuttonpause.connect (self.playersetbuttonpause)
		self.playerworker.setloopsignal.connect (self.playerworker.setloop)

#		self.player.started.connect (self.playerworker.startworker)
#		self.playerworker.finished.connect (self.player.quit)
		self.playerworker.startworker()
		self.playerworker.finished.connect (self.playerworker.deleteLater)
#		self.player.finished.connect (self.player.deleteLater)

#		QtGui.qApp.aboutToQuit.connect (self.player.quit)
#		QtGui.qApp.aboutToQuit.connect (self.player.wait)

#		self.player.start()

	@QtCore.Slot()
	def on_buttonloadfile_clicked (self):

		self.playerfile = QtGui.QFileDialog.getOpenFileName (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		if self.playerfile:
			self.playerworker.playurisignal.emit (self.playerfile)
			self.ui.labelfilmtitle.setText (QtCore.QFileInfo (self.playerfile).fileName())

	@QtCore.Slot (unicode)
	def updatelabelduration (self, text):
		self.ui.labelduration.setText (text)

	@QtCore.Slot (int)
	def updatesliderseek (self, value):
		self.ui.sliderseek.blockSignals (True)
		self.ui.sliderseek.setValue (value)
		self.ui.sliderseek.blockSignals (False)

	@QtCore.Slot (unicode)
	def updatelineedit (self, text):
		if self.updatelineeditblocked:
			return

		if self.splitchoose == SplitNotChosen:
			return
		elif self.splitchoose == SplitAdjustStart:
			self.ui.lineeditstarttime.setText (text)
		elif self.splitchoose == SplitAdjustStop:
			self.ui.lineeditendtime.setText (text)

	@QtCore.Slot (int)
	def updateslidervolume (self, value):
		self.ui.slidervolume.blockSignals (True)
		self.ui.slidervolume.setValue (value)
		self.ui.slidervolume.blockSignals (False)

		self.on_slidervolume_valueChanged (value)

	@QtCore.Slot (int)
	def on_slidervolume_valueChanged (self, value):

		volmax = self.ui.slidervolume.maximum()
		volmin = self.ui.slidervolume.minimum()

		if value == 0:
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/mute.png'))
		elif value < (volmin + (volmax - volmin) / 3):
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/volume.png'))
		elif value < (volmin + (volmax - volmin) * 2 / 3):
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/weakvolume.png'))
		else:
			self.ui.buttonvolume.setIcon (QtGui.QIcon (':/images/strongvolume.png'))

	@QtCore.Slot()
	def playersetbuttonplay (self):
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/play.png'))

	@QtCore.Slot()
	def playersetbuttonpause (self):
		self.ui.buttonplayerplay.setIcon (QtGui.QIcon (':/images/pause2.png'))

	@QtCore.Slot()
	def on_buttoncancelbrowse_clicked (self):
		self.playerworker.setloopsignal.emit (0, 0)

		self.ui.buttoncancelbrowse.hide()
		self.ui.buttonpreview.show()

		self.updatelineeditblocked = False
		self.ui.lineeditstarttime.setEnabled (True)
		self.ui.lineeditendtime.setEnabled (True)
		
	@QtCore.Slot()
	def on_buttonpreview_clicked (self):

		self.updatelineeditblocked = True
		self.ui.lineeditstarttime.setEnabled (False)
		self.ui.lineeditendtime.setEnabled (False)

		starttime = str2time (self.ui.lineeditstarttime.text())
		stoptime = str2time (self.ui.lineeditendtime.text())
		if starttime < 0 or stoptime <= starttime:
			return

		self.playerworker.setloopsignal.emit (self.ui.lineeditstarttime.text(), self.ui.lineeditendtime.text())

		self.ui.buttonpreview.hide()
		self.ui.buttoncancelbrowse.show()

	def createmerger (self):

		self.mergerworker = VideoMerger()
		self.merger = QtCore.QThread()
		self.mergerworker.moveToThread (self.merger)

		self.mergerworker.appendtasksignal.connect (self.mergerworker.appendtask)
		self.mergerworker.switchrowsignal.connect (self.mergerworker.switchrow)
		self.mergerworker.removerowsignal.connect (self.mergerworker.removerow)

		self.mergerworker.startsignal.connect (self.mergerworker.startworker)
		self.mergerworker.updatemodel.connect (self.updatemergemodel)
		self.mergerworker.finished.connect (self.merger.quit)
		self.mergerworker.finished.connect (self.mergerworker.deleteLater)
		self.merger.finished.connect (self.merger.deleteLater)

		QtGui.qApp.aboutToQuit.connect (self.merger.quit)
		QtGui.qApp.aboutToQuit.connect (self.merger.wait)

	@QtCore.Slot()
	def on_buttonplus_clicked (self):

		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		model = self.ui.mergeview.model()

		while len (files) > 0:
			newfile = QtCore.QFileInfo (files.pop (0))

			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), newfile.fileName())
			model.setData (model.index (row, 3), (0, self.tr ("Not Started")))

			self.ui.labelmerge.setText (self.tr ("There are %d video clips to be merged.") % (row + 1))

			checkerworker = MediaFileChecker (newfile.absoluteFilePath(), len (self.checkers))
			checker = QtCore.QThread()
			checkerworker.moveToThread (checker)

			checkerworker.discoveredsignal.connect (self.mediafilediscovered)
			checker.started.connect (checkerworker.startworker)
			checkerworker.finished.connect (checker.quit)
			checkerworker.finished.connect (checkerworker.deleteLater)
			checker.finished.connect (self.checker.deleteLater)

			QtGui.qApp.aboutToQuit.connect (self.checker.quit)
			QtGui.qApp.aboutToQuit.connect (self.checker.wait)

			checker.start()

			self.checkers.append ({"worker": checkerworker, "thread": checker, "operation": "Merge", "row": row, "file": newfile})

	@QtCore.Slot()
	def on_buttonup_clicked (self):
		row = self.ui.mergeview.currentIndex().row()
		model = self.ui.mergeview.model()

		if row == 0:
			return
		
		model.insertRow (row - 1, model.takeRow (row))
		self.mergerworker.switchrowsignal.emit (row, row - 1)
		self.ui.mergeview.setCurrentIndex (model.index (row - 1, 0))

	@QtCore.Slot()
	def on_buttondown_clicked (self):
		row = self.ui.mergeview.currentIndex().row()
		model = self.ui.mergeview.model()

		if row >= model.rowCount() - 1:
			return

		model.insertRow (row + 1, model.takeRow (row))
		self.mergerworker.switchrowsignal.emit (row, row + 1)
		self.ui.mergeview.setCurrentIndex (model.index (row + 1, 0))

	@QtCore.Slot()
	def on_buttondelete_clicked (self):
		row = self.ui.mergeview.currentIndex().row()
		self.ui.mergeview.model().takeRow (row)
		self.mergerworker.removerowsignal.emit (row)

	@QtCore.Slot()
	def on_buttonstart_clicked (self):
		self.mergerworker.startsignal.emit (self.ui.lineeditfilenameblank.text(), self.ui.lineeditsaveblank.text())

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		pass

	@QtCore.Slot()
	def on_buttonexamine_clicked (self):
		exam = MergeExam (self.ui.lineeditfilenameblank.text(), self.ui.lineeditsaveblank.text())
		exam.move (self.pos() + self.rect().center() - exam.rect().center())
		exam.exec_()

	@QtCore.Slot (int, list)
	def updatemergemodel (self, row, value):
		model = self.ui.mergeview.model()
		rownum = model.rowCount()

		if row >= rownum:
			return

		if value is not None:
			model.setData (model.index (row, 3), value)

	@QtCore.Slot()
	def on_buttonsave_clicked (self):
		if not self.playerfile:
			return

		starttime = str2time (self.ui.lineeditstarttime.text())
		stoptime = str2time (self.ui.lineeditendtime.text())
		duration = stoptime - starttime
		if starttime < 0 or duration <= 0:
			return

		model = self.ui.transview.model()
		row = model.rowCount()
		model.insertRow (row)

		model.setData (model.index (row, 0), self.playerfile)
		model.setData (model.index (row, 1), 0)
		model.setData (model.index (row, 2), self.tr ("Not Started"))

		outputname = QtGui.QFileDialog.getSaveFileName (self, self.tr ("Save destination"))[0]
		if not outputname:
			return

		model.setData (model.index (row, 3), outputname)

		splitterworker = VideoSplitter (self.playerfile, outputname, time2str (starttime), time2str (duration), row)
		splitter = QtCore.QThread()
		splitterworker.moveToThread (splitter)

		splitter.started.connect (splitterworker.startworker)
		splitterworker.updatemodel.connect (self.updatetransmodel)
		splitterworker.finished.connect (splitter.quit)
		splitterworker.finished.connect (splitterworker.deleteLater)
		splitter.finished.connect (self.splitter.deleteLater)

		QtGui.qApp.aboutToQuit.connect (self.splitter.quit)
		QtGui.qApp.aboutToQuit.connect (self.splitter.wait)

		splitter.start()

		self.transcoding.append ({"thread": splitter, "worker": splitterworker, "status": TransTaskProcessing})

	@QtCore.Slot (int, list)
	def updatetransmodel (self, row, value):
		model = self.ui.transview.model()
		rownum = model.rowCount()

		if row >= rownum:
			return

		if value[0] is not None:
			model.setData (model.index (row, 1), value[0])

			if value[0] >= 100:
				self.transcoding [row] ["status"] = TransTaskFinished
				model.setData (model.index (row, 2), self.tr ("Finished"))

				if self.translisting == TransTaskProcessing:
					self.ui.transview.setRowHidden (row, QtCore.QModelIndex(), True)
				else:
					self.ui.transview.setRowHidden (row, QtCore.QModelIndex(), False)

		if value[1] is not None:
			model.setData (model.index (row, 2), value[1])

	def closeEvent (self, event):
		if self.trayicon.isVisible():
			self.hide()
			event.ignore()

	@QtCore.Slot()
	def on_buttontransnew_clicked (self):

		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MusicLocation))[0]
		newpath = QtGui.QFileDialog.getExistingDirectory (self, self.tr ("Select output directory"))
		model = self.ui.transview.model()

		while len (files) > 0:
			newfile = QtCore.QFileInfo (files.pop (0))
			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), newfile.fileName())
			model.setData (model.index (row, 1), 0)
			model.setData (model.index (row, 2), self.tr ("Not Started"))

			if newpath == "":
				newpath = newfile.absolutePath()
			model.setData (model.index (row, 3), newpath)

			dstfile = newpath + "/" + newfile.baseName() + "-change.mp4"

			transcodeworker = Transcoder (newfile.absoluteFilePath(), dstfile, row)
			transcode = QtCore.QThread()
			transcodeworker.moveToThread (transcode)

			transcodeworker.playsignal.connect (transcodeworker.play)
			transcodeworker.pausesignal.connect (transcodeworker.pause)
			transcodeworker.removesignal.connect (transcodeworker.remove)
			transcodeworker.updatemodel.connect (self.updatetransmodel)

			transcode.started.connect (transcodeworker.startworker)
			transcodeworker.finished.connect (transcode.quit)
			transcodeworker.finished.connect (transcodeworker.deleteLater)
			transcodeworker.finished.connect (self.splitter.deleteLater)

			QtGui.qApp.aboutToQuit.connect (transcodeworker.quit)
			QtGui.qApp.aboutToQuit.connect (transcodeworker.wait)

			transcode.start()

			self.transcoding.append ({"thread": transcode, "worker": transcodeworker, "status": TransTaskProcessing})

	@QtCore.Slot()
	def on_buttontransbegin_clicked (self):
		row = self.ui.transview.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["worker"].playsignal.emit()

	@QtCore.Slot()
	def on_buttontranspause_clicked (self):
		row = self.ui.transview.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["worker"].pausesignal.emit()

	@QtCore.Slot()
	def on_buttontransdelete_clicked (self):
		row = self.ui.transview.currentIndex().row()
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["worker"].removesignal.emit()
		self.transcoding [row] ["status"] = TransTaskDeleted
		self.ui.transview.setRowHidden (row, QtCore.QModelIndex(), True)

	@QtCore.Slot()
	def on_listWidget_itemClicked (self):
		self.translisting = self.ui.listWidget.currentRow()

		for row in xrange (self.ui.transview.model().rowCount()):
			if self.transcoding [row] ["status"] == self.translisting:
				self.ui.transview.setRowHidden (row, QtCore.QModelIndex(), False)
			else:
				self.ui.transview.setRowHidden (row, QtCore.QModelIndex(), True)

	@QtCore.Slot()
	def on_buttonbrowse_clicked (self):
		self.ui.lineeditsaveblank.setText (QtGui.QFileDialog.getExistingDirectory (self, self.tr ("Select output directory")))

	@QtCore.Slot()
	def on_MovieEdit_clicked (self):
		self.ui.stackedWidget.setCurrentIndex (0)

	@QtCore.Slot()
	def on_FormatConvert_clicked (self):
		self.ui.stackedWidget.setCurrentIndex (1)

	@QtCore.Slot()
	def on_buttonvideomerge_clicked (self):
		self.ui.stackedWidget_2.setCurrentIndex (1)

	@QtCore.Slot()
	def on_buttonvideointerceptpage_clicked (self):
		self.ui.stackedWidget_2.setCurrentIndex (0)

	@QtCore.Slot (int, list)
	def mediafilediscovered (self, row, params):

		if row >= len (self.checkers):
			return

		checker = self.checkers[row]

		if checker["operation"] == "Merge":

			if params[0] is None or params[1] is None or params[2] is None:
				return

			model = self.ui.mergeview.model()
			model.setData (model.index (row, 1), "%s" % (time2str (params[2])))
			model.setData (model.index (row, 2), "%d X %d" % (params[0], params[1]))

			self.mergerworker.appendtasksignal.emit (checker["file"].absoluteFilePath(), checker["row"])

	def eventFilter (self, obj, event):
		if event.type() == QtCore.QEvent.FocusIn and not self.updatelineeditblocked:
			if obj == self.ui.lineeditstarttime:
				self.splitchoose = SplitAdjustStart
			elif obj == self.ui.lineeditendtime:
				self.splitchoose = SplitAdjustStop

		return QtGui.QWidget.eventFilter (self, obj, event)

	def mouseMoveEvent (self, event):
		super (MainWindow, self).mouseMoveEvent (event)
		if self.leftclicked == True:
			self.move (event.globalPos() - self.startdragging)

	def mousePressEvent (self, event):
		super (MainWindow, self).mousePressEvent (event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftclicked = True
			self.startdragging = event.globalPos() - self.pos()
			self.clickedpos = event.globalPos()

	def mouseReleaseEvent (self, event):
		super (MainWindow, self).mouseReleaseEvent (event)
		self.leftclicked = False

	def mouseDoubleClickEvent (self, event):
		super (MainWindow, self).mouseDoubleClickEvent (event)
		self.on_buttonmaximize_clicked()

	def frameMouseRelease (self, event):
		super (MainWindow, self).mouseReleaseEvent (event)
		if event.button() == QtCore.Qt.LeftButton and event.globalPos() == self.clickedpos:
			self.leftclicked = False
			self.ui.buttonplayerplay.clicked.emit()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())
		painter = QtGui.QPainter()
		painter.begin (pixmap)
		painter.fillRect (pixmap.rect(), QtCore.Qt.white)
		painter.setBrush (QtCore.Qt.black)
		painter.drawRoundRect (pixmap.rect(), 3, 3)
		painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))
