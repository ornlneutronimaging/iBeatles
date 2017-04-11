# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ui_strainMapping.ui'
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
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(310, 60))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 80))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.d0_units_label = QtGui.QLabel(self.groupBox)
        self.d0_units_label.setGeometry(QtCore.QRect(282, 31, 63, 16))
        self.d0_units_label.setObjectName(_fromUtf8("d0_units_label"))
        self.d0_label = QtGui.QLabel(self.groupBox)
        self.d0_label.setGeometry(QtCore.QRect(15, 31, 16, 16))
        self.d0_label.setObjectName(_fromUtf8("d0_label"))
        self.d0_label_2 = QtGui.QLabel(self.groupBox)
        self.d0_label_2.setGeometry(QtCore.QRect(148, 31, 16, 16))
        self.d0_label_2.setObjectName(_fromUtf8("d0_label_2"))
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_2.setGeometry(QtCore.QRect(172, 31, 100, 21))
        self.lineEdit_2.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setGeometry(QtCore.QRect(38, 31, 100, 21))
        self.lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(218, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.recap_tabs = QtGui.QTabWidget(self.centralwidget)
        self.recap_tabs.setObjectName(_fromUtf8("recap_tabs"))
        self.strain_mapping_tab = QtGui.QWidget()
        self.strain_mapping_tab.setObjectName(_fromUtf8("strain_mapping_tab"))
        self.recap_tabs.addTab(self.strain_mapping_tab, _fromUtf8(""))
        self.sigma_tab = QtGui.QWidget()
        self.sigma_tab.setObjectName(_fromUtf8("sigma_tab"))
        self.recap_tabs.addTab(self.sigma_tab, _fromUtf8(""))
        self.alpha_tab = QtGui.QWidget()
        self.alpha_tab.setObjectName(_fromUtf8("alpha_tab"))
        self.recap_tabs.addTab(self.alpha_tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.recap_tabs)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(17, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setMinimumSize(QtCore.QSize(80, 0))
        self.label.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.transparency_slider = QtGui.QSlider(self.centralwidget)
        self.transparency_slider.setProperty("value", 50)
        self.transparency_slider.setOrientation(QtCore.Qt.Horizontal)
        self.transparency_slider.setObjectName(_fromUtf8("transparency_slider"))
        self.horizontalLayout_2.addWidget(self.transparency_slider)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.recap_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Strain Mapping", None))
        self.groupBox.setTitle(_translate("MainWindow", "Unstrained d-spacing", None))
        self.d0_units_label.setText(_translate("MainWindow", "Angstroms", None))
        self.d0_label.setText(_translate("MainWindow", "d0", None))
        self.d0_label_2.setText(_translate("MainWindow", "+/-", None))
        self.pushButton.setText(_translate("MainWindow", "Export Image ...", None))
        self.recap_tabs.setTabText(self.recap_tabs.indexOf(self.strain_mapping_tab), _translate("MainWindow", "Strain Mapping", None))
        self.recap_tabs.setTabText(self.recap_tabs.indexOf(self.sigma_tab), _translate("MainWindow", "Sigma", None))
        self.recap_tabs.setTabText(self.recap_tabs.indexOf(self.alpha_tab), _translate("MainWindow", "Alpha", None))
        self.label.setText(_translate("MainWindow", "Transparency", None))

