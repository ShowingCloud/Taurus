#!/usr/bin/python

import sys, os, time
from PySide import QtCore, QtGui
from ctypes import pythonapi, c_void_p, py_object

import gobject

from UI import Ui_MainWindow
from Frontend import MergeExam, NewConvert, SaveSplit, LoadError, SplitProg, CommonError
from Backend import Player, VideoSplitter, VideoMerger, MediaFileChecker, Transcoder
from Toolkit import TransferDelegate, MergeDelegate, time2str, str2time


TransTaskVerifying, TransTaskProcessing, TransTaskFinished, TransTaskDeleted = xrange (4)
MergeTaskVerifying, MergeTaskReadyToProcess, MergeTaskFinished, MergeTaskDeleted = xrange (4)
SplitNotChosen, SplitAdjustStart, SplitAdjustStop = xrange (3)


class MainWindow (QtGui.QMainWindow):

	def __init__ (self, rpc, rpcworker, params, parent = None):
		QtGui.QMainWindow.__init__ (self, parent)

		self.rpc = rpc
		self.rpcworker = rpcworker
		self.rpcworker.lostconnection.connect (self.lostconnection)
		self.params = params

		self.ui = Ui_MainWindow()
		self.ui.setupUi (self)
		self.setWindowFlags (QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowMinimizeButtonHint)

		self.setWindowTitle (self.tr ("Cartoon Encoding and Uploading Platform"))
		self.setWindowIcon (QtGui.QIcon (':/images/icon.png'))

		self.createActions()
		self.createplayer()
		self.createmerger()
		self.createUIdetails()
		self.creategobject()

		self.transcoding = list()
		self.translisting = TransTaskProcessing
		self.mergelist = list()
		self.checkers = list()
		self.splitchoose = SplitNotChosen
		self.playerfile = None

		self.leftclicked = False

	def createActions (self):
		self.restact = QtGui.QAction (self.tr ("&Restore"), self, triggered = self.showNormal)
		self.minact = QtGui.QAction (self.tr ("Mi&nimize"), self, triggered = self.showMinimized)
		self.maxact = QtGui.QAction (self.tr ("Ma&ximize"), self, triggered = self.showMaximized)
		self.quitact = QtGui.QAction (self.tr ("&Quit"), self, triggered = QtGui.qApp.quit)

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
		self.ui.transview.setContextMenuPolicy (QtCore.Qt.CustomContextMenu)

		self.ui.mergeview.setModel (self.mergemodel (self))
		self.ui.mergeview.setRootIsDecorated (False)
		self.ui.mergeview.setAlternatingRowColors (True)
		self.ui.mergeview.setItemDelegate (MergeDelegate (self))

		self.ui.stackedWidget.setCurrentIndex (0)

		self.ui.lineeditstarttime.installEventFilter (self)
		self.ui.lineeditendtime.installEventFilter (self)
		self.ui.lineeditleadertitle.installEventFilter (self)

		self.params.setdefault ('LastPlayerPath', '')
		self.params.setdefault ('LastSplitTime', '')
		self.params.setdefault ('LastSplitFile', '')
		self.params.setdefault ('LastSplitPath', '')
		self.params.setdefault ('LastMergePath', '')
		self.params.setdefault ('LastMergeSrcPath', '')
		self.params.setdefault ('LastTransferPath', '')
		self.params.setdefault ('LastTransferSrcPath', '')
		self.params.setdefault ('NumEdited', 0)
		self.params.setdefault ('NumTransferred', 0)

		self.ui.labelvideoedit.setText (self.tr ("Video Edit: %d") % (self.params['NumEdited']))
		self.ui.labelvideoconvert.setText (self.tr ("Video Transfer: %d") % (self.params['NumTransferred']))

		self.ui.labellastrecordtime.setText (self.params['LastSplitTime'])
		self.ui.labellastsavefile.setText (self.params['LastSplitFile'])
		self.ui.lineeditsaveblank.setText (self.params['LastMergePath'])

		self.ui.buttoncancelbrowse.hide()

		self.ui.labelfilmtitle.setAlignment (QtCore.Qt.AlignHCenter)

	def creategobject (self):
		gobject.threads_init()
		self.mainloop = gobject.MainLoop()
		self.context = self.mainloop.get_context()

		self.p = self.context.pending
		self.t = self.context.iteration
		self.e = QtGui.qApp.processEvents

		self.contexttimer = QtCore.QTimer (QtGui.QApplication.instance())
		self.contexttimer.timeout.connect (self.contexthandler)
		self.contexttimer.start (10)

	@QtCore.Slot()
	def contexthandler (self): # optimized or not?
		p = self.p
		t = self.t
		e = self.e
		for i in xrange (100):
			if p():
				t()
			else:
				break

		e()

	@QtCore.Slot()
	def lostconnection (self):
		msg = CommonError (self.tr ("Lost connection to server. Exiting..."))
		msg.exec_()
		QtGui.qApp.quit()

	@QtCore.Slot (QtCore.QPoint)
	def on_transview_customContextMenuRequested (self, point):
		row = self.ui.transview.currentIndex().row()
		if row >= len (self.transcoding) or row < 0:
			return

		menu = QtGui.QMenu (self)
		menu.addAction (QtGui.QAction (self.tr ("Start"), self, triggered = self.singletransbegin))
		menu.addAction (QtGui.QAction (self.tr ("Pause"), self, triggered = self.singletranspause))
		menu.addAction (QtGui.QAction (self.tr ("Delete"), self, triggered = self.on_buttontransdelete_clicked))
		menu.exec_ (QtGui.QCursor.pos())

	@QtCore.Slot (unicode)
	def newmerged (self, path):
		self.params['NumEdited'] += 1
		self.ui.labelvideoedit.setText (self.tr ("Video Edit: %d") % (self.params['NumEdited']))
		self.params['LastMergePath'] = path
		self.ui.lineeditsaveblank.setText (path)

		self.rpcworker.newmergedsignal.emit (self.params)

	@QtCore.Slot (unicode, unicode, unicode)
	def newsplitted (self, time, filename, path):
		self.params['NumEdited'] += 1
		self.ui.labelvideoedit.setText (self.tr ("Video Edit: %d") % (self.params['NumEdited']))
		self.params['LastSplitTime'] = time
		self.ui.labellastrecordtime.setText (time)
		self.params['LastSplitFile'] = filename
		self.ui.labellastsavefile.setText (filename)
		self.params['LastSplitPath'] = path

		self.rpcworker.newsplittedsignal.emit (self.params)

	@QtCore.Slot (unicode)
	def newtransferred (self, path, srcpath):
		self.params['NumTransferred'] += 1
		self.ui.labelvideoconvert.setText (self.tr ("Video Transfer: %d") % (self.params['NumTransferred']))
		self.params['LastTransferPath'] = path
		self.params['LastTransferSrcPath'] = srcpath

		self.rpcworker.newtransferredsignal.emit (self.params)

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
		if self.isMaximized():
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

		self.player = Player (self.windowId, self.ui.sliderseek.minimum(), self.ui.sliderseek.maximum(), self.ui.slidervolume.minimum(), self.ui.slidervolume.maximum())

		self.ui.buttonplayerplay.clicked.connect (self.player.playclickedsignal)
		self.ui.buttonplayerstop.clicked.connect (self.player.stopclickedsignal)
		self.ui.buttonplayerbackward.clicked.connect (self.player.backwardclickedsignal)
		self.ui.buttonplayerforward.clicked.connect (self.player.forwardclickedsignal)
		self.ui.buttonvolume.clicked.connect (self.player.muteornotsignal)
		self.ui.sliderseek.valueChanged.connect (self.player.sliderseekvaluesignal)
		self.ui.slidervolume.valueChanged.connect (self.player.slidervolumevaluesignal)

		self.player.updatelabelduration.connect (self.updatelabelduration)
		self.player.updatesliderseek.connect (self.updatesliderseek)
		self.player.updateslidervolume.connect (self.updateslidervolume)
		self.player.updatelineedit.connect (self.updatelineedit)
		self.player.setbuttonplay.connect (self.playersetbuttonplay)
		self.player.setbuttonpause.connect (self.playersetbuttonpause)

		self.player.startworker()

	@QtCore.Slot()
	def on_buttonloadfile_clicked (self):

		if os.path.isdir (self.params['LastPlayerPath']):
			lastpath = self.params['LastPlayerPath']
		else:
			lastpath = QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MoviesLocation)

		self.playerfile = QtGui.QFileDialog.getOpenFileName (self, self.tr ("Open"), lastpath)[0]
		if self.playerfile:
			checker = MediaFileChecker (self.playerfile, len (self.checkers))
			checker.discoveredsignal.connect (self.mediafilediscovered)
			checker.finished.connect (checker.deleteLater)
			self.checkers.append ({"worker": checker, "operation": "Player", "params": self.playerfile})
			checker.startworker()

			self.params['LastPlayerPath'] = QtCore.QDir.toNativeSeparators (QtCore.QFileInfo (self.playerfile).absolutePath())
			self.rpcworker.renewparamssignal.emit (self.params)

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
		self.player.setloopsignal.emit (0, 0)

		self.ui.buttoncancelbrowse.hide()
		self.ui.buttonpreview.show()

		self.ui.lineeditstarttime.setEnabled (True)
		self.ui.lineeditendtime.setEnabled (True)
		
	@QtCore.Slot()
	def on_buttonpreview_clicked (self):

		self.splitchoose = SplitNotChosen
		self.ui.lineeditstarttime.setEnabled (False)
		self.ui.lineeditendtime.setEnabled (False)

		starttime = str2time (self.ui.lineeditstarttime.text())
		stoptime = str2time (self.ui.lineeditendtime.text())
		if starttime < 0 or stoptime <= starttime:
			msg = CommonError (self.tr ("Start time or stop time invalid."))
			msg.exec_()
			self.ui.buttoncancelbrowse.clicked.emit()
			return

		self.player.setloopsignal.emit (self.ui.lineeditstarttime.text(), self.ui.lineeditendtime.text())

		self.ui.buttonpreview.hide()
		self.ui.buttoncancelbrowse.show()

	def createmerger (self):

		self.merger = VideoMerger (self)

		self.merger.removerowsignal.connect (self.removemergerow)
		self.merger.updatemodel.connect (self.updatemergemodel)
		self.merger.finished.connect (self.unblockmergeelements)
		self.merger.finished.connect (self.flushmergelist)
		self.merger.filenamedecided.connect (self.updatefilename)

		self.merger.startnewmerge.connect (self.newmerged)

	@QtCore.Slot()
	def on_buttonplus_clicked (self):

		if os.path.isdir (self.params['LastMergeSrcPath']):
			lastpath = self.params['LastMergeSrcPath']
		else:
			lastpath = QtGui.QDesktopServices.storageLocation (QtGui.QDesktopServices.MoviesLocation)

		files = QtGui.QFileDialog.getOpenFileNames (self, self.tr ("Open"), lastpath)[0]
		if len (files) == 0:
			return

		self.params['LastMergeSrcPath'] = QtCore.QDir.toNativeSeparators (QtCore.QFileInfo (files[0]).absolutePath())
		self.rpcworker.renewparamssignal.emit (self.params)

		model = self.ui.mergeview.model()

		while len (files) > 0:
			newfile = QtCore.QFileInfo (files.pop (0))

			row = model.rowCount()
			model.insertRow (row)

			model.setData (model.index (row, 0), newfile.fileName())
			model.setData (model.index (row, 3), (0, self.tr ("Not Started")))

			rownum = 1
			for i in xrange (row):
				if self.mergelist[i] == MergeTaskReadyToProcess or self.mergelist[i] == MergeTaskVerifying:
					rownum += 1
			self.ui.labelmerge.setText (self.tr ("There are %d video clips to be merged.") % rownum)

			checker = MediaFileChecker (QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()), len (self.checkers))
			checker.discoveredsignal.connect (self.mediafilediscovered)
			checker.finished.connect (checker.deleteLater)
			self.merger.appendtasksignal.emit (QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()))
			self.checkers.append ({"worker": checker, "operation": "Merge", "params": row})
			self.mergelist.append (MergeTaskVerifying)
			checker.startworker()

	@QtCore.Slot()
	def on_buttonup_clicked (self):
		prevrow = row = self.ui.mergeview.currentIndex().row()
		model = self.ui.mergeview.model()

		if not self.mergelist[row] == MergeTaskReadyToProcess:
			return

		while prevrow > 0:
			prevrow -= 1
			if self.mergelist[prevrow] == MergeTaskReadyToProcess:
				break

		if prevrow < 0 or prevrow == row:
			return
		
		model.insertRow (prevrow, model.takeRow (row))
		self.mergelist[row], self.mergelist[prevrow] = self.mergelist[prevrow], self.mergelist[row]
		self.merger.switchrowsignal.emit (row, prevrow)
		self.ui.mergeview.setCurrentIndex (model.index (prevrow, 0))

	@QtCore.Slot()
	def on_buttondown_clicked (self):
		nextrow = row = self.ui.mergeview.currentIndex().row()
		model = self.ui.mergeview.model()

		if not self.mergelist[row] == MergeTaskReadyToProcess:
			return

		while nextrow < model.rowCount() - 1:
			nextrow += 1
			if self.mergelist[nextrow] == MergeTaskReadyToProcess:
				break

		if nextrow >= model.rowCount() or nextrow == row:
			return

		model.insertRow (nextrow, model.takeRow (row))
		self.mergelist[row], self.mergelist[nextrow] = self.mergelist[nextrow], self.mergelist[row]
		self.merger.switchrowsignal.emit (row, nextrow)
		self.ui.mergeview.setCurrentIndex (model.index (nextrow, 0))

	@QtCore.Slot()
	def on_buttondelete_clicked (self):
		row = self.ui.mergeview.currentIndex().row()
		self.merger.removerowsignal.emit (row)

	@QtCore.Slot()
	def on_buttonstart_clicked (self):
		filename = self.ui.lineeditfilenameblank.text()
		path = self.ui.lineeditsaveblank.text()

		if filename == "":
			msg = CommonError (self.tr ("Please input output filename"))
			msg.exec_()
			return
		elif len (filename) > 255:
			msg = CommonError (self.tr ("Filename too long."))
			msg.exec_()
			return
		
		if path == "":
			msg = CommonError (self.tr ("Please input output path"))
			msg.exec_()
			return

		self.merger.startsignal.emit (filename, path)
		self.blockmergeelements()

	@QtCore.Slot()
	def on_buttoncancel_clicked (self):
		self.merger.cancelsignal.emit()
		self.unblockmergeelements()

	@QtCore.Slot()
	def on_buttonexamine_clicked (self):
		exam = MergeExam (self.ui.lineeditfilenameblank.text(), self.ui.lineeditsaveblank.text())
		exam.move (self.pos() + self.rect().center() - exam.rect().center())
		exam.exec_()

	def blockmergeelements (self):
		self.ui.mergeview.setEnabled (False)
		self.ui.buttonstart.setEnabled (False)
		self.ui.buttonplus.setEnabled (False)
		self.ui.buttonup.setEnabled (False)
		self.ui.buttondown.setEnabled (False)
		self.ui.buttondelete.setEnabled (False)
		self.ui.lineeditfilenameblank.setEnabled (False)
		self.ui.lineeditsaveblank.setEnabled (False)
		self.ui.buttonbrowse.setEnabled (False)
		self.ui.buttonexamine.setEnabled (False)

	@QtCore.Slot()
	def unblockmergeelements (self):
		self.ui.mergeview.setEnabled (True)
		self.ui.buttonstart.setEnabled (True)
		self.ui.buttonplus.setEnabled (True)
		self.ui.buttonup.setEnabled (True)
		self.ui.buttondown.setEnabled (True)
		self.ui.buttondelete.setEnabled (True)
		self.ui.lineeditfilenameblank.setEnabled (True)
		self.ui.lineeditsaveblank.setEnabled (True)
		self.ui.buttonbrowse.setEnabled (True)
		self.ui.buttonexamine.setEnabled (True)

	@QtCore.Slot()
	def flushmergelist (self):
		for row in xrange (self.ui.mergeview.model().rowCount()):
			self.merger.removerowsignal.emit (row)

	@QtCore.Slot (unicode)
	def updatefilename (self, filename):
		self.ui.lineeditfilenameblank.setText (filename)

	@QtCore.Slot (int)
	def removemergerow (self, row):
		self.mergelist[row] = MergeTaskDeleted
		self.ui.mergeview.setRowHidden (row, QtCore.QModelIndex(), True)

		rownum = 0
		for i in xrange (self.ui.mergeview.model().rowCount()):
			if self.mergelist[i] == MergeTaskReadyToProcess or self.mergelist[i] == MergeTaskVerifying:
				rownum += 1
		self.ui.labelmerge.setText (self.tr ("There are %d video clips to be merged.") % rownum)

	@QtCore.Slot (int, int)
	def updatemergemodel (self, row, value):
		model = self.ui.mergeview.model()
		rownum = model.rowCount()

		if row >= rownum:
			for i in xrange (rownum):
				model.setData (model.index (i, 3), (100, self.tr ("Finished")))
			return

		if value is not None:
			if model.data (model.index (row, 3))[0] < value:
				if value < 100:
					model.setData (model.index (row, 3), (value, self.tr ("Processing...")))
				else:
					model.setData (model.index (row, 3), (100, self.tr ("Finished")))

			for i in xrange (row):
				model.setData (model.index (i, 3), (100, self.tr ("Finished")))

	@QtCore.Slot (unicode)
	def on_lineeditleadertitle_textChanged (self, text):
		self.ui.checkboxleadertitle.setChecked (True)

	@QtCore.Slot()
	def on_buttonsave_clicked (self):
		if not self.playerfile:
			return

		self.splitchoose = SplitNotChosen

		starttime = str2time (self.ui.lineeditstarttime.text())
		stoptime = str2time (self.ui.lineeditendtime.text())
		duration = stoptime - starttime
		if starttime < 0 or duration <= 0:
			msg = CommonError (self.tr ("Start time or stop time invalid."))
			msg.exec_()
			return

		if self.ui.checkboxleadertitle.isChecked():
			title = self.ui.lineeditleadertitle.text()
			if len (title) > 63:
				msg = CommonError (self.tr ("Movie title too long."))
				msg.exec_()
				return
		else:
			title = None

		timestring = "%s -- %s" % (time2str (starttime), time2str (stoptime))

		ss = SaveSplit (self.params['LastSplitPath'])
		ss.move (self.pos() + self.rect().center() - ss.rect().center())
		if not ss.exec_() == QtGui.QDialog.Accepted:
			return

		outputfile = os.path.join (ss.splitpath, ss.splitfile)

		self.splitter = VideoSplitter (self.playerfile, outputfile, starttime, duration, title, ss.totranscode, self.player.params, self)
		self.splitter.addtranscode.connect (self.addtranscode)
		self.splitter.startnewsplit.connect (self.newsplitted)
		self.splitter.startworker (timestring)

		self.splitprog = SplitProg()
		self.splitprog.move (self.pos() + self.rect().center() - self.splitprog.rect().center())
		self.splitter.updatemodel.connect (self.splitprog.setprogressbar)
		self.splitter.finished.connect (self.splitprog.accept)

		if not self.splitprog.exec_() == QtGui.QDialog.Accepted:
			self.splitter.finished.emit()

	@QtCore.Slot (int, tuple)
	def updatetransmodel (self, row, value):
		model = self.ui.transview.model()
		rownum = model.rowCount()

		if row >= rownum:
			return

		if value[0] is not None:
			if model.data (model.index (row, 1)) < value[0]:
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

		model = self.ui.transview.model()

		nc = NewConvert (self.params['LastTransferPath'], self.params['LastTransferSrcPath'])
		if nc.exec_() == QtGui.QDialog.Accepted:

			files = nc.files
			newpath = nc.transferpath

			self.params['LastTransferPath'] = newpath
			self.rpcworker.renewparamssignal.emit (self.params)

			while len (files) > 0:
				newfile = QtCore.QFileInfo (files.pop (0))
				row = model.rowCount()
				model.insertRow (row)

				model.setData (model.index (row, 0), newfile.fileName())
				model.setData (model.index (row, 1), 0)
				model.setData (model.index (row, 2), self.tr ("Verifying File Parameters..."))
				model.setData (model.index (row, 3), newpath)

				checker = MediaFileChecker (QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()), len (self.checkers))
				checker.discoveredsignal.connect (self.mediafilediscovered)
				checker.finished.connect (checker.deleteLater)
				self.checkers.append ({"worker": checker, "operation": "Transcode",
					"params": (QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()), newpath, row, self)})
				self.transcoding.append ({"worker": None, "status": TransTaskVerifying})
				checker.startworker()

	@QtCore.Slot (unicode)
	def addtranscode (self, filename):
		model = self.ui.transview.model()
		newfile = QtCore.QFileInfo (filename)
		row = model.rowCount()
		model.insertRow (row)
		path = QtCore.QDir.toNativeSeparators (newfile.absolutePath())

		model.setData (model.index (row, 0), newfile.fileName())
		model.setData (model.index (row, 1), 0)
		model.setData (model.index (row, 2), self.tr ("Transcoding..."))
		model.setData (model.index (row, 3), path)

		transcode = Transcoder (QtCore.QDir.toNativeSeparators (newfile.absoluteFilePath()), path, row, self)

		transcode.playsignal.connect (transcode.play)
		transcode.pausesignal.connect (transcode.pause)
		transcode.removesignal.connect (transcode.remove)
		transcode.updatemodel.connect (self.updatetransmodel)
		transcode.finished.connect (transcode.deleteLater)
		transcode.startnewtransfer.connect (self.newtransferred)

		transcode.startworker()
		self.transcoding.append ({"worker": transcode, "status": TransTaskProcessing})

	@QtCore.Slot()
	def on_buttontransbegin_clicked (self):
		for i in xrange (self.ui.transview.model().rowCount()):
			if self.transcoding [i] ["status"] == TransTaskProcessing:
				self.transcoding [i] ["worker"].playsignal.emit()

	@QtCore.Slot()
	def singletransbegin (self):
		row = self.ui.transview.currentIndex().row()
		if row >= len (self.transcoding):
			return
		if self.transcoding [row] ["status"] == TransTaskProcessing:
			self.transcoding [row] ["worker"].playsignal.emit()

	@QtCore.Slot()
	def on_buttontranspause_clicked (self):
		for i in xrange (self.ui.transview.model().rowCount()):
			if self.transcoding [i] ["status"] == TransTaskProcessing:
				self.transcoding [i] ["worker"].pausesignal.emit()

	@QtCore.Slot()
	def singletranspause (self):
		row = self.ui.transview.currentIndex().row()
		if row >= len (self.transcoding):
			return
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
		self.translisting = self.ui.listWidget.currentRow() == 0 and TransTaskProcessing or TransTaskFinished

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

	@QtCore.Slot (int, bool, dict)
	def mediafilediscovered (self, row, verified, params):

		if row >= len (self.checkers):
			return

		checker = self.checkers[row]

		if not verified:
			le = LoadError()
			le.move (self.pos() + self.rect().center() - le.rect().center())
			le.exec_()
#			le.show()

		if checker["operation"] == "Merge":

			mergerow = checker["params"]
			model = self.ui.mergeview.model()

			if not verified:
				model.setData (model.index (mergerow, 1), "%s" % (self.tr ("Video Source Criteria Not Met")))
				model.setData (model.index (mergerow, 2), "")
				self.removemergerow (mergerow)

				rownum = 0
				for i in xrange (model.rowCount()):
					if self.mergelist[i] == MergeTaskReadyToProcess or self.mergelist[i] == MergeTaskVerifying:
						rownum += 1
				self.ui.labelmerge.setText (self.tr ("There are %d video clips to be merged.") % rownum)

			else:
				model.setData (model.index (mergerow, 1), "%s" % (time2str (params.get ("length"))))
				model.setData (model.index (mergerow, 2), "%d X %d" % (params.get ("videowidth"), params.get ("videoheight")))
				self.mergelist[mergerow] = MergeTaskReadyToProcess

			self.merger.verifiedtasksignal.emit (mergerow, params, verified)

		elif checker["operation"] == "Player":

			if verified:
				self.player.params = params
				self.player.playurisignal.emit (checker["params"])
				self.ui.labelfilmtitle.setText (QtCore.QFileInfo (checker["params"]).fileName())

		elif checker["operation"] == "Transcode":

			transrow = checker["params"][2]

			if not verified:
				self.transcoding [transrow]["status"] = TransTaskDeleted
				self.ui.transview.setRowHidden (transrow, QtCore.QModelIndex(), True)
				return

			transcode = Transcoder (*checker["params"])

			transcode.playsignal.connect (transcode.play)
			transcode.pausesignal.connect (transcode.pause)
			transcode.removesignal.connect (transcode.remove)
			transcode.updatemodel.connect (self.updatetransmodel)
			transcode.finished.connect (transcode.deleteLater)
			transcode.startnewtransfer.connect (self.newtransferred)

			transcode.startworker()
			self.transcoding [transrow]["worker"] = transcode
			self.transcoding [transrow]["status"] = TransTaskProcessing

		del checker

	def eventFilter (self, obj, event):
		if event.type() == QtCore.QEvent.FocusIn:
			if obj == self.ui.lineeditstarttime:
				self.splitchoose = SplitAdjustStart
			elif obj == self.ui.lineeditendtime:
				self.splitchoose = SplitAdjustStop
			elif obj == self.ui.lineeditleadertitle:
				self.splitchoose = SplitNotChosen

		elif event.type() == QtCore.QEvent.KeyPress:
			if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
				if obj == self.ui.lineeditstarttime:
					self.player.seekstarttimesignal.emit (self.ui.lineeditstarttime.text())
				elif obj == self.ui.lineeditleadertitle:
					self.ui.buttonsave.clicked.emit()

		return QtGui.QWidget.eventFilter (self, obj, event)

	def mouseMoveEvent (self, event):
		super (MainWindow, self).mouseMoveEvent (event)

		if self.leftclicked == True:

			if self.isMaximized():
				self.ui.buttonmaximize.setIcon (QtGui.QIcon (':/images/maximize.png'))

				origsize = self.rect().size()
				self.showNormal()
				newsize = self.rect().size()

				xfactor = float (newsize.width()) / origsize.width()
				yfactor = float (newsize.height()) / origsize.height()

				self.startdragging.setX (self.startdragging.x() * xfactor)
				self.startdragging.setY (self.startdragging.y() * yfactor)

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
		self.ui.buttonmaximize.clicked.emit()

	def frameMouseRelease (self, event):
		super (MainWindow, self).mouseReleaseEvent (event)
		if event.button() == QtCore.Qt.LeftButton and event.globalPos() == self.clickedpos:
			self.leftclicked = False
			self.ui.buttonplayerplay.clicked.emit()

	def resizeEvent (self, event):
		pixmap = QtGui.QPixmap (self.size())

		if not self.isMaximized():
			painter = QtGui.QPainter()
			painter.begin (pixmap)
			painter.fillRect (pixmap.rect(), QtCore.Qt.white)
			painter.setBrush (QtCore.Qt.black)
			painter.drawRoundRect (pixmap.rect(), 3, 3)
			painter.end()

		self.setMask (pixmap.createMaskFromColor (QtCore.Qt.white))
