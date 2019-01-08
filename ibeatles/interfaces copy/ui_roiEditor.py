# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_roiEditor.ui'
#
# Created: Sat Dec  3 10:20:26 2016
#      by: PyQt4 UI code generator 4.11.3
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
        MainWindow.resize(446, 418)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.add_roi_button = QtGui.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.add_roi_button.setFont(font)
        self.add_roi_button.setObjectName(_fromUtf8("add_roi_button"))
        self.horizontalLayout.addWidget(self.add_roi_button)
        self.remove_roi_button = QtGui.QPushButton(self.centralwidget)
        self.remove_roi_button.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.remove_roi_button.setFont(font)
        self.remove_roi_button.setObjectName(_fromUtf8("remove_roi_button"))
        self.horizontalLayout.addWidget(self.remove_roi_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 446, 22))
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
        QtCore.QObject.connect(self.add_roi_button, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.add_roi_button_clicked)
        QtCore.QObject.connect(self.remove_roi_button, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.remove_roi_button_clicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Label", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "X0", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Y0", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Width", None))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Height", None))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Groups", None))
        self.add_roi_button.setText(_translate("MainWindow", "+", None))
        self.remove_roi_button.setText(_translate("MainWindow", "-", None))
        self.action1_Data.setText(_translate("MainWindow", "1. Data", None))
        self.action2_Normalization.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Binning.setText(_translate("MainWindow", "4. Binning", None))
        self.action4_Fitting.setText(_translate("MainWindow", "5. Fitting", None))
        self.action5_Results.setText(_translate("MainWindow", "6. Strain Mapping", None))
        self.actionAbout.setText(_translate("MainWindow", "About ...", None))
        self.action1_Raw_Data.setText(_translate("MainWindow", "1. Raw Data", None))
        self.action2_Normalization_2.setText(_translate("MainWindow", "2. Normalization", None))
        self.action3_Normalized_Data.setText(_translate("MainWindow", "3. Normalized Data", None))

