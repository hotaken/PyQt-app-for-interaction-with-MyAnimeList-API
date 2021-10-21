import os
from PyQt5 import QtWidgets, QtGui, QtCore
import PyQt5
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMessageBox, QPlainTextEdit, QVBoxLayout
import sys

from requests.models import HTTPError
import mainwindow
import utils
import MalAPI
import urllib
import dialogAnime


class ImgWidget(QLabel):
    def __init__(self, parent=None, url=None):
        super(ImgWidget, self).__init__(parent)
        try:
            data = urllib.request.urlopen(url).read()
            image = QtGui.QImage()
            image.loadFromData(data)
            self.pic = QtGui.QPixmap(image).scaled(112, 172)
        except:
            self.pic = QtGui.QPixmap(112, 172)
            self.pic.fill(QtGui.QColorConstants.White)

        self.setPixmap(self.pic)


class AuthorizationDialog(QDialog):

    def __init__(self, url, *args, **kwargs):
        "Create a new dialogue instance."
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Authorization")
        self.url = url
        self.gui_init()

    def gui_init(self):
        "Create and establish the widget layout."
        self.link = QLabel()
        self.link.setOpenExternalLinks(True)
        self.link.setText(
            f"<a href=\"{self.url}\">Authorize</a>")
        self.code = QPlainTextEdit()
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel("Authorize your application by clicking here:"))
        layout.addWidget(self.link)
        layout.addWidget(QLabel("Code from redirected window:"))
        layout.addWidget(self.code)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class DialogAnime(dialogAnime.Ui_DialogAnime, QtWidgets.QDialog):
    def __init__(self, title: str, synopsis: str, picture: ImgWidget, status: str, score: str) -> None:
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.labelPicture.setPixmap(picture.pic)
        self.setWindowTitle(title)
        self.labelSynopsis.setPlainText(synopsis)

        if score == '':
            self.comboBoxScore.setCurrentIndex(0)
        else:
            self.comboBoxScore.setCurrentIndex(int(score))

        if status == 'completed':
            self.radioButtonCompleted.setChecked(True)
        else:
            self.radioButtonNotWatched.setChecked(True)
            self.comboBoxScore.setEnabled(False)

        self.radioButtonCompleted.clicked.connect(
            lambda: self.radioButtonChanged(mode=1))
        self.radioButtonNotWatched.clicked.connect(
            lambda: self.radioButtonChanged(mode=0))

        self.labelSynopsis.setReadOnly(True)

    def radioButtonChanged(self, mode):
        if mode:
            self.comboBoxScore.setEnabled(True)
            self.radioButtonNotWatched.setChecked(False)
        else:
            self.comboBoxScore.setCurrentIndex(0)
            self.comboBoxScore.setEnabled(False)
            self.radioButtonCompleted.setChecked(False)


class App(mainwindow.Ui_MainWindow, QtWidgets.QMainWindow):
    malapi = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.textSearch.textChanged.connect(self.textSearchTextChanged)
        self.textSearch.returnPressed.connect(self.textSearchReturnPressed)
        self.btnSearch.clicked.connect(self.searchBtnClick)
        self.listSearch.setColumnCount(7)
        self.listSearch.setHorizontalHeaderLabels([
            "id",
            "Picture",
            "Name",
            "Score",
            "Your score",
            "Your status"
        ])
        self.listSearch.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.listSearch.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.listSearch.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        self.listList.setColumnCount(7)
        self.listList.setHorizontalHeaderLabels([
            "id",
            "Picture",
            "Name",
            "Score",
            "Your score",
            "Your status"
        ])
        self.listList.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.listList.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.listList.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        self.tabWidget.currentChanged.connect(self.onTabChange)

        self.listSearch.cellDoubleClicked.connect(
            lambda index_row, index_col: self.onTableLineClick(index_row, 0))
        self.listList.cellDoubleClicked.connect(
            lambda index_row, index_col: self.onTableLineClick(index_row, 1))

    def textSearchReturnPressed(self):
        self.btnSearch.click()

    def onTabChange(self, i):
        if i == 1:
            self.updateListTable()

    def textSearchTextChanged(self):
        if len(self.textSearch.text()) > 100:
            self.textSearch.setText(self.textSearch.text()[0:100])
            self.textSearch.moveCursor(QtGui.QTextCursor.End)
        elif len(self.textSearch.text()) < 3 and len(self.textSearch.text()) != 0:
            self.btnSearch.setEnabled(False)
        else:
            self.btnSearch.setEnabled(True)

    def getToken(self, path='token'):
        try:
            self.malapi = MalAPI.MALAPI()
        except RuntimeError as er:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText(er.args[0])
            msg.setWindowTitle("Error")
            msg.exec_()
            sys.exit()
        while True:
            if self.malapi.load_token(path):
                try:
                    self.malapi.print_user_info()
                    break
                except:
                    os.remove(path)
                    msgBox = AuthorizationDialog(self.malapi.authorization_url)
                    result = msgBox.exec_()
                    if not result:
                        sys.exit()
                    authorization_code = msgBox.code.toPlainText()
                    try:
                        self.malapi.make_token(authorization_code)
                        break
                    except:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setText(
                            "Service is not available or your authorization code is invalid")
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        continue
            else:
                msgBox = AuthorizationDialog(self.malapi.authorization_url)
                result = msgBox.exec_()
                if not result:
                    sys.exit()
                authorization_code = msgBox.code.toPlainText()
                try:
                    self.malapi.make_token(authorization_code)
                    break
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setText(
                        "Service is not available or your authorization code is invalid")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    continue

    @ utils.throttle(seconds=5)
    def updateListTable(self):
        print('updateListTable')
        self.listList.setRowCount(0)
        try:
            self.listJson = self.malapi.get_user_animelist()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText(
                "Service is not available")
            msg.setWindowTitle("Error")
            msg.exec_()

        for node in self.listJson:
            row_index = self.listList.rowCount()
            self.listList.insertRow(row_index)
            item = node['node']

            id = item['id']
            title = item['title']
            picture_url = item['main_picture']['medium']
            synopsis = item['synopsis']
            score = item['mean'] if 'mean' in item else ''
            user_status = ''
            user_score = ''
            if 'my_list_status' in item:
                user_status = item['my_list_status']['status']
                user_score = item['my_list_status']['score']
                user_score = str(user_score) if (user_score != 0) else ''
            user_status = user_status if(user_status != '') else 'not watched'

            self.listList.setItem(
                row_index, 0, QtWidgets.QTableWidgetItem(str(id)))
            self.listList.setCellWidget(
                row_index, 1, ImgWidget(self, picture_url))
            self.listList.setItem(
                row_index, 2, QtWidgets.QTableWidgetItem(title))
            self.listList.setItem(
                row_index, 3, QtWidgets.QTableWidgetItem(str(score)))
            self.listList.setItem(
                row_index, 4, QtWidgets.QTableWidgetItem(str(user_score)))
            self.listList.setItem(
                row_index, 5, QtWidgets.QTableWidgetItem(user_status))
            self.listList.setItem(
                row_index, 6, QtWidgets.QTableWidgetItem(synopsis))
        self.listList.hideColumn(6)
        # self.listList.resizeColumnsToContents()
        self.listList.resizeRowsToContents()

    @ utils.throttle(seconds=5)
    def updateSearchTable(self, search_str=""):
        print('updateSearchTable')
        self.listSearch.setRowCount(0)
        try:
            if search_str == "":
                self.searchJson = self.malapi.get_top_anime()
            else:
                self.searchJson = self.malapi.find_anime(search_str)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText(
                "Service is not available")
            msg.setWindowTitle("Error")
            msg.exec_()

        for node in self.searchJson:
            row_index = self.listSearch.rowCount()
            self.listSearch.insertRow(row_index)
            item = node['node']

            id = item['id']
            title = item['title']
            picture_url = item['main_picture']['medium']
            synopsis = item['synopsis']
            score = item['mean'] if 'mean' in item else ''
            user_status = ''
            user_score = ''
            if 'my_list_status' in item:
                user_status = item['my_list_status']['status']
                user_score = item['my_list_status']['score']
                user_score = str(user_score) if (user_score != 0) else ''
            user_status = user_status if(user_status != '') else 'not watched'

            self.listSearch.setItem(
                row_index, 0, QtWidgets.QTableWidgetItem(str(id)))
            self.listSearch.setCellWidget(
                row_index, 1, ImgWidget(self, picture_url))
            self.listSearch.setItem(
                row_index, 2, QtWidgets.QTableWidgetItem(title))
            self.listSearch.setItem(
                row_index, 3, QtWidgets.QTableWidgetItem(str(score)))
            self.listSearch.setItem(
                row_index, 4, QtWidgets.QTableWidgetItem(str(user_score)))
            self.listSearch.setItem(
                row_index, 5, QtWidgets.QTableWidgetItem(user_status))
            self.listSearch.setItem(
                row_index, 6, QtWidgets.QTableWidgetItem(synopsis))
        self.listSearch.hideColumn(6)
        self.listSearch.resizeRowsToContents()
        # self.listSearch.resizeColumnsToContents()

    def searchBtnClick(self):
        if self.textSearch.text() != '':
            self.updateSearchTable(self.textSearch.text())
        else:
            self.updateSearchTable()

    def onTableLineClick(self, index_row, table_number):
        table = None
        if table_number == 0:
            table = self.listSearch
        elif table_number == 1:
            table = self.listList
        id = table.item(index_row, 0).text()
        picture = table.cellWidget(index_row, 1)
        title = table.item(index_row, 2).text()
        score = table.item(index_row, 3).text()
        user_score = table.item(index_row, 4).text()
        user_status = table.item(index_row, 5).text()
        synopsis = table.item(index_row, 6).text()

        editWindow = DialogAnime(
            title, synopsis, picture, user_status, user_score)
        result = editWindow.exec_()
        try:
            if not result:
                return
            if editWindow.radioButtonCompleted.isChecked():
                new_user_status = 'completed'
                new_user_score = editWindow.comboBoxScore.currentIndex()
            else:
                new_user_status = 'not watched'
                new_user_score = 0
            if new_user_score == user_score and new_user_status == user_status:
                return
            else:
                if new_user_status == 'not watched':
                    self.malapi.delete_anime_from_list(id)
                    if table_number == 1:
                        table.removeRow(index_row)
                        return
                    table.item(index_row, 4).setText('')
                    table.item(index_row, 5).setText(new_user_status)

                else:
                    self.malapi.add_anime_to_list(id, new_user_score)
                    new_user_score = '' if (
                        new_user_score == 0) else str(new_user_score)
                    table.item(index_row, 4).setText(new_user_score)
                    table.item(index_row, 5).setText(new_user_status)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText(
                "Service is not available")
            msg.setWindowTitle("Error")
            msg.exec_()


def application():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    window.getToken()
    window.updateSearchTable()

    sys.exit(app.exec_())


if __name__ == '__main__':
    application()
