# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_mainWindow.ui'
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
        MainWindow.resize(1495, 906)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1495, 22))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy)
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuSteps = QtGui.QMenu(self.menubar)
        self.menuSteps.setObjectName(_fromUtf8("menuSteps"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        self.dockWidget.setMinimumSize(QtCore.QSize(150, 38))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget)
        self.dockWidget_2 = QtGui.QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(_fromUtf8("dockWidget_2"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_2)
        self.dockWidget_3 = QtGui.QDockWidget(MainWindow)
        self.dockWidget_3.setObjectName(_fromUtf8("dockWidget_3"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_3)
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
        self.menuSteps.addAction(self.action1_Raw_Data)
        self.menuSteps.addAction(self.action2_Normalization_2)
        self.menuSteps.addAction(self.action3_Normalized_Data)
        self.menuSteps.addAction(self.action3_Binning)
        self.menuSteps.addAction(self.action4_Fitting)
        self.menuSteps.addAction(self.action5_Results)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuSteps.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "1 - Load Data", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "2 - Normalization", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "3 - Normalized Data", None))
        self.menuSteps.setTitle(_translate("MainWindow", "Steps", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "4 - Binning", None))
        self.dockWidget_2.setWindowTitle(_translate("MainWindow", "5 - Fitting", None))
        self.dockWidget_3.setWindowTitle(_translate("MainWindow", "6 - Strain Mapping", None))
        self.action1_Data.setText(_translate("MainWindow", "1. Data", None))
        self.action2_Normalization.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Binning.setText(_translate("MainWindow", "4. Binning", None))
        self.action4_Fitting.setText(_translate("MainWindow", "5. Fitting", None))
        self.action5_Results.setText(_translate("MainWindow", "6. Strain Mapping", None))
        self.actionAbout.setText(_translate("MainWindow", "About ...", None))
        self.action1_Raw_Data.setText(_translate("MainWindow", "1. Raw Data", None))
        self.action2_Normalization_2.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Normalized_Data.setText(_translate("MainWindow", "3. Normalized Data", None))

