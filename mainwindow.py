# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Projects\MALAPI\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_search = QtWidgets.QWidget()
        self.tab_search.setObjectName("tab_search")
        self.listSearch = QtWidgets.QTableWidget(self.tab_search)
        self.listSearch.setGeometry(QtCore.QRect(0, 60, 776, 491))
        self.listSearch.setColumnCount(0)
        self.listSearch.setObjectName("listSearch")
        self.listSearch.setRowCount(0)
        self.btnSearch = QtWidgets.QPushButton(self.tab_search)
        self.btnSearch.setGeometry(QtCore.QRect(410, 10, 111, 40))
        self.btnSearch.setObjectName("btnSearch")
        self.textSearch = QtWidgets.QLineEdit(self.tab_search)
        self.textSearch.setGeometry(QtCore.QRect(10, 10, 361, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textSearch.setFont(font)
        self.textSearch.setObjectName("textSearch")
        self.tabWidget.addTab(self.tab_search, "")
        self.tab_list = QtWidgets.QWidget()
        self.tab_list.setObjectName("tab_list")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_list)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listList = QtWidgets.QTableWidget(self.tab_list)
        self.listList.setObjectName("listList")
        self.listList.setColumnCount(0)
        self.listList.setRowCount(0)
        self.verticalLayout.addWidget(self.listList)
        self.tabWidget.addTab(self.tab_list, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionAdd_to_list = QtWidgets.QAction(MainWindow)
        self.actionAdd_to_list.setObjectName("actionAdd_to_list")
        self.actionDelete_from_list = QtWidgets.QAction(MainWindow)
        self.actionDelete_from_list.setObjectName("actionDelete_from_list")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MALAPI"))
        self.btnSearch.setText(_translate("MainWindow", "Search"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_search), _translate("MainWindow", "Search"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_list), _translate("MainWindow", "List"))
        self.actionAdd_to_list.setText(_translate("MainWindow", "Add to list"))
        self.actionDelete_from_list.setText(_translate("MainWindow", "Delete from list"))
