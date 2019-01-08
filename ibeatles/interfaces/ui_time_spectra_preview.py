# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_time_spectra_preview.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1331, 848)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.time_spectra_text = QtWidgets.QTextEdit(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.time_spectra_text.sizePolicy().hasHeightForWidth())
        self.time_spectra_text.setSizePolicy(sizePolicy)
        self.time_spectra_text.setMinimumSize(QtCore.QSize(0, 0))
        self.time_spectra_text.setMaximumSize(QtCore.QSize(250, 16777215))
        self.time_spectra_text.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.time_spectra_text.setObjectName("time_spectra_text")
        self.time_spectra_plot = MPLWidget(self.splitter)
        self.time_spectra_plot.setObjectName("time_spectra_plot")
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1331, 22))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action1_Data = QtWidgets.QAction(MainWindow)
        self.action1_Data.setObjectName("action1_Data")
        self.action2_Normalization = QtWidgets.QAction(MainWindow)
        self.action2_Normalization.setEnabled(True)
        self.action2_Normalization.setObjectName("action2_Normalization")
        self.action3_Binning = QtWidgets.QAction(MainWindow)
        self.action3_Binning.setObjectName("action3_Binning")
        self.action4_Fitting = QtWidgets.QAction(MainWindow)
        self.action4_Fitting.setObjectName("action4_Fitting")
        self.action5_Results = QtWidgets.QAction(MainWindow)
        self.action5_Results.setObjectName("action5_Results")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.action1_Raw_Data = QtWidgets.QAction(MainWindow)
        self.action1_Raw_Data.setObjectName("action1_Raw_Data")
        self.action2_Normalization_2 = QtWidgets.QAction(MainWindow)
        self.action2_Normalization_2.setObjectName("action2_Normalization_2")
        self.action3_Normalized_Data = QtWidgets.QAction(MainWindow)
        self.action3_Normalized_Data.setObjectName("action3_Normalized_Data")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.action1_Data.setText(_translate("MainWindow", "1. Data"))
        self.action2_Normalization.setText(_translate("MainWindow", "2. Normalization"))
        self.action3_Binning.setText(_translate("MainWindow", "4. Binning"))
        self.action4_Fitting.setText(_translate("MainWindow", "5. Fitting"))
        self.action5_Results.setText(_translate("MainWindow", "6. Strain Mapping"))
        self.actionAbout.setText(_translate("MainWindow", "About ..."))
        self.action1_Raw_Data.setText(_translate("MainWindow", "1. Raw Data"))
        self.action2_Normalization_2.setText(_translate("MainWindow", "2. Normalization"))
        self.action3_Normalized_Data.setText(_translate("MainWindow", "3. Normalized Data"))

from .mplwidget import MPLWidget
