# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_binningWindow.ui'
#
# Created: Wed Mar 22 11:10:18 2017
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
        MainWindow.resize(860, 617)
        MainWindow.setMinimumSize(QtCore.QSize(300, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.left_widget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_widget.sizePolicy().hasHeightForWidth())
        self.left_widget.setSizePolicy(sizePolicy)
        self.left_widget.setObjectName(_fromUtf8("left_widget"))
        self.horizontalLayout_2.addWidget(self.left_widget)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(200, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.selection_x0 = QtGui.QLineEdit(self.groupBox)
        self.selection_x0.setObjectName(_fromUtf8("selection_x0"))
        self.gridLayout.addWidget(self.selection_x0, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.selection_y0 = QtGui.QLineEdit(self.groupBox)
        self.selection_y0.setObjectName(_fromUtf8("selection_y0"))
        self.gridLayout.addWidget(self.selection_y0, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.selection_width = QtGui.QLineEdit(self.groupBox)
        self.selection_width.setObjectName(_fromUtf8("selection_width"))
        self.gridLayout.addWidget(self.selection_width, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.selection_height = QtGui.QLineEdit(self.groupBox)
        self.selection_height.setObjectName(_fromUtf8("selection_height"))
        self.gridLayout.addWidget(self.selection_height, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(200, 0))
        self.groupBox_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pixel_bin_size = QtGui.QLineEdit(self.groupBox_2)
        self.pixel_bin_size.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pixel_bin_size.setObjectName(_fromUtf8("pixel_bin_size"))
        self.horizontalLayout.addWidget(self.pixel_bin_size)
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.selection_x0, QtCore.SIGNAL(_fromUtf8("editingFinished()")), MainWindow.roi_selection_widgets_modified)
        QtCore.QObject.connect(self.selection_y0, QtCore.SIGNAL(_fromUtf8("editingFinished()")), MainWindow.roi_selection_widgets_modified)
        QtCore.QObject.connect(self.selection_width, QtCore.SIGNAL(_fromUtf8("editingFinished()")), MainWindow.roi_selection_widgets_modified)
        QtCore.QObject.connect(self.selection_height, QtCore.SIGNAL(_fromUtf8("editingFinished()")), MainWindow.roi_selection_widgets_modified)
        QtCore.QObject.connect(self.pixel_bin_size, QtCore.SIGNAL(_fromUtf8("editingFinished()")), MainWindow.roi_selection_widgets_modified)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox.setTitle(_translate("MainWindow", "Selection", None))
        self.label.setText(_translate("MainWindow", "Xo:", None))
        self.selection_x0.setText(_translate("MainWindow", "0", None))
        self.label_2.setText(_translate("MainWindow", "Yo:", None))
        self.selection_y0.setText(_translate("MainWindow", "0", None))
        self.label_3.setText(_translate("MainWindow", "Width:", None))
        self.selection_width.setText(_translate("MainWindow", "20", None))
        self.label_4.setText(_translate("MainWindow", "Height:", None))
        self.selection_height.setText(_translate("MainWindow", "20", None))
        self.groupBox_2.setTitle(_translate("MainWindow", "Bins Size", None))
        self.pixel_bin_size.setText(_translate("MainWindow", "10", None))
        self.label_5.setText(_translate("MainWindow", "pixel x pixel", None))

import icons_rc
