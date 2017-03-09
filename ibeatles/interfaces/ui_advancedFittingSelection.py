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
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.selection_table = QtGui.QTableWidget(self.tab)
        self.selection_table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.selection_table.setObjectName(_fromUtf8("selection_table"))
        self.selection_table.setColumnCount(0)
        self.selection_table.setRowCount(0)
        self.verticalLayout.addWidget(self.selection_table)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.lock_table = QtGui.QTableWidget(self.tab_2)
        self.lock_table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.lock_table.setObjectName(_fromUtf8("lock_table"))
        self.lock_table.setColumnCount(0)
        self.lock_table.setRowCount(0)
        self.verticalLayout_3.addWidget(self.lock_table)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.tabWidget)
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
        self.advanced_selection_cell_size_slider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.advanced_selection_cell_size_slider.setObjectName(_fromUtf8("advanced_selection_cell_size_slider"))
        self.horizontalLayout_4.addWidget(self.advanced_selection_cell_size_slider)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.apply_button = QtGui.QPushButton(self.centralwidget)
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.horizontalLayout_4.addWidget(self.apply_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.advanced_selection_cell_size_slider, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), MainWindow.selection_cell_size_changed)
        QtCore.QObject.connect(self.apply_button, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.apply_button_clicked)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_2.setText(_translate("MainWindow", "All Bins selected in this table will be used to display the Counts vs Lambda plot", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Active", None))
        self.label_3.setText(_translate("MainWindow", "All Bins selected in this table will be locked (their fitting parameters can not be modified).", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Lock", None))
        self.label.setText(_translate("MainWindow", "Cells Size", None))
        self.apply_button.setText(_translate("MainWindow", "Apply", None))

import icons_rc
