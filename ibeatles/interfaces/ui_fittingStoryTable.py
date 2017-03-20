# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_fittingStoryTable.ui'
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
        MainWindow.resize(889, 553)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.story_table = QtGui.QTableWidget(self.centralwidget)
        self.story_table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.story_table.setObjectName(_fromUtf8("story_table"))
        self.story_table.setColumnCount(7)
        self.story_table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.story_table.setHorizontalHeaderItem(6, item)
        self.verticalLayout.addWidget(self.story_table)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.add_row_button = QtGui.QPushButton(self.centralwidget)
        self.add_row_button.setMinimumSize(QtCore.QSize(40, 30))
        self.add_row_button.setMaximumSize(QtCore.QSize(40, 30))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.add_row_button.setFont(font)
        self.add_row_button.setObjectName(_fromUtf8("add_row_button"))
        self.horizontalLayout.addWidget(self.add_row_button)
        self.remove_row_button = QtGui.QPushButton(self.centralwidget)
        self.remove_row_button.setMinimumSize(QtCore.QSize(40, 30))
        self.remove_row_button.setMaximumSize(QtCore.QSize(40, 30))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.remove_row_button.setFont(font)
        self.remove_row_button.setObjectName(_fromUtf8("remove_row_button"))
        self.horizontalLayout.addWidget(self.remove_row_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.start_fits_button = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_fits_button.sizePolicy().hasHeightForWidth())
        self.start_fits_button.setSizePolicy(sizePolicy)
        self.start_fits_button.setMinimumSize(QtCore.QSize(100, 20))
        self.start_fits_button.setMaximumSize(QtCore.QSize(300, 40))
        self.start_fits_button.setObjectName(_fromUtf8("start_fits_button"))
        self.horizontalLayout.addWidget(self.start_fits_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 889, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Fitting Story", None))
        self.label.setText(_translate("MainWindow", "Check Variables to Fit", None))
        item = self.story_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "D_spacing", None))
        item = self.story_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Sigma", None))
        item = self.story_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Alpha", None))
        item = self.story_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "A1", None))
        item = self.story_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "A2", None))
        item = self.story_table.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "A5", None))
        item = self.story_table.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "A6", None))
        self.add_row_button.setText(_translate("MainWindow", "+", None))
        self.remove_row_button.setText(_translate("MainWindow", "-", None))
        self.start_fits_button.setText(_translate("MainWindow", "Start Fits", None))

