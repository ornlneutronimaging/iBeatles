# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_advancedFittingSelection.ui'
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
        MainWindow.resize(946, 766)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.checkBox = QtGui.QCheckBox(self.groupBox)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout_2.addWidget(self.checkBox)
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout_2.addWidget(self.checkBox_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.selection_table = QtGui.QTableWidget(self.centralwidget)
        self.selection_table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.selection_table.setObjectName(_fromUtf8("selection_table"))
        self.selection_table.setColumnCount(0)
        self.selection_table.setRowCount(0)
        self.verticalLayout.addWidget(self.selection_table)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_4.addWidget(self.label)
        self.advanced_selection_cell_size_slider = QtGui.QSlider(self.centralwidget)
        self.advanced_selection_cell_size_slider.setMinimum(10)
        self.advanced_selection_cell_size_slider.setMaximum(50)
        self.advanced_selection_cell_size_slider.setProperty("value", 20)
        self.advanced_selection_cell_size_slider.setOrientation(QtCore.Qt.Horizontal)
        self.advanced_selection_cell_size_slider.setObjectName(_fromUtf8("advanced_selection_cell_size_slider"))
        self.horizontalLayout_4.addWidget(self.advanced_selection_cell_size_slider)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.apply_button = QtGui.QPushButton(self.centralwidget)
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.horizontalLayout_4.addWidget(self.apply_button)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.advanced_selection_cell_size_slider, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), MainWindow.selection_cell_size_changed)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox.setTitle(_translate("MainWindow", "Selection Type", None))
        self.checkBox.setText(_translate("MainWindow", "Add Bin(s) to Counts vs Lambda Plot", None))
        self.checkBox_2.setText(_translate("MainWindow", "Lock Bin(s)", None))
        self.label.setText(_translate("MainWindow", "Cells Size", None))
        self.apply_button.setText(_translate("MainWindow", "Apply", None))

import icons_rc
