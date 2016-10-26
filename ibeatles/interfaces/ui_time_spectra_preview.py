# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_time_spectra_preview.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1331, 848)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.textEdit = QtGui.QTextEdit(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit.setMaximumSize(QtCore.QSize(300, 16777215))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.widget = MPLWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1331, 22))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy)
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action1_Data = QtGui.QAction(MainWindow)
        self.action1_Data.setObjectName(_fromUtf8("action1_Data"))
        self.action2_Normalization = QtGui.QAction(MainWindow)
        self.action2_Normalization.setEnabled(True)
        self.action2_Normalization.setObjectName(_fromUtf8("action2_Normalization"))
        self.action3_Binning = QtGui.QAction(MainWindow)
        self.action3_Binning.setObjectName(_fromUtf8("action3_Binning"))
        self.action4_Fitting = QtGui.QAction(MainWindow)
        self.action4_Fitting.setObjectName(_fromUtf8("action4_Fitting"))
        self.action5_Results = QtGui.QAction(MainWindow)
        self.action5_Results.setObjectName(_fromUtf8("action5_Results"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.action1_Raw_Data = QtGui.QAction(MainWindow)
        self.action1_Raw_Data.setObjectName(_fromUtf8("action1_Raw_Data"))
        self.action2_Normalization_2 = QtGui.QAction(MainWindow)
        self.action2_Normalization_2.setObjectName(_fromUtf8("action2_Normalization_2"))
        self.action3_Normalized_Data = QtGui.QAction(MainWindow)
        self.action3_Normalized_Data.setObjectName(_fromUtf8("action3_Normalized_Data"))

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.action1_Data.setText(_translate("MainWindow", "1. Data", None))
        self.action2_Normalization.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Binning.setText(_translate("MainWindow", "4. Binning", None))
        self.action4_Fitting.setText(_translate("MainWindow", "5. Fitting", None))
        self.action5_Results.setText(_translate("MainWindow", "6. Strain Mapping", None))
        self.actionAbout.setText(_translate("MainWindow", "About ...", None))
        self.action1_Raw_Data.setText(_translate("MainWindow", "1. Raw Data", None))
        self.action2_Normalization_2.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Normalized_Data.setText(_translate("MainWindow", "3. Normalized Data", None))

from .mplwidget import MPLWidget
