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
        MainWindow.resize(583, 431)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(100, 0))
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.total_columns_value = QtGui.QLabel(self.groupBox)
        self.total_columns_value.setObjectName(_fromUtf8("total_columns_value"))
        self.gridLayout.addWidget(self.total_columns_value, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setMinimumSize(QtCore.QSize(100, 0))
        self.label_4.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.total_rows_value = QtGui.QLabel(self.groupBox)
        self.total_rows_value.setObjectName(_fromUtf8("total_rows_value"))
        self.gridLayout.addWidget(self.total_rows_value, 1, 1, 1, 1)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.option_selected = QtGui.QRadioButton(self.groupBox_2)
        self.option_selected.setObjectName(_fromUtf8("option_selected"))
        self.verticalLayout.addWidget(self.option_selected)
        self.option_locked = QtGui.QRadioButton(self.groupBox_2)
        self.option_locked.setObjectName(_fromUtf8("option_locked"))
        self.verticalLayout.addWidget(self.option_locked)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.rows_value = QtGui.QLineEdit(self.groupBox_2)
        self.rows_value.setObjectName(_fromUtf8("rows_value"))
        self.horizontalLayout.addWidget(self.rows_value)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.and_or_selection = QtGui.QComboBox(self.groupBox_2)
        self.and_or_selection.setObjectName(_fromUtf8("and_or_selection"))
        self.and_or_selection.addItem(_fromUtf8(""))
        self.and_or_selection.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.and_or_selection)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_8 = QtGui.QLabel(self.groupBox_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_2.addWidget(self.label_8)
        self.columns_value = QtGui.QLineEdit(self.groupBox_2)
        self.columns_value.setObjectName(_fromUtf8("columns_value"))
        self.horizontalLayout_2.addWidget(self.columns_value)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_2.addWidget(self.label_7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.graphical_selection_button = QtGui.QPushButton(self.centralwidget)
        self.graphical_selection_button.setObjectName(_fromUtf8("graphical_selection_button"))
        self.horizontalLayout_4.addWidget(self.graphical_selection_button)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.apply_button = QtGui.QPushButton(self.centralwidget)
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.horizontalLayout_4.addWidget(self.apply_button)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox.setTitle(_translate("MainWindow", "Infos", None))
        self.label.setText(_translate("MainWindow", "Total Columns:", None))
        self.total_columns_value.setText(_translate("MainWindow", "N/A", None))
        self.label_4.setText(_translate("MainWindow", "Total Rows:", None))
        self.total_rows_value.setText(_translate("MainWindow", "N/A", None))
        self.groupBox_2.setTitle(_translate("MainWindow", "Selection", None))
        self.option_selected.setText(_translate("MainWindow", "Selected (used in Counts vs TOF plot)", None))
        self.option_locked.setText(_translate("MainWindow", "Locked (fitting can not be modified)", None))
        self.label_5.setText(_translate("MainWindow", "Row(s)", None))
        self.label_6.setText(_translate("MainWindow", "ex: 1,4-5", None))
        self.and_or_selection.setItemText(0, _translate("MainWindow", "OR", None))
        self.and_or_selection.setItemText(1, _translate("MainWindow", "AND", None))
        self.label_8.setText(_translate("MainWindow", "Column(s)", None))
        self.label_7.setText(_translate("MainWindow", "ex: 1,4-5", None))
        self.graphical_selection_button.setText(_translate("MainWindow", "Graphical Selection ...", None))
        self.apply_button.setText(_translate("MainWindow", "Apply", None))

import icons_rc
