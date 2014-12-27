__copyright__ = "Copyright 2014 Davide Olianas (ubuntupk@gmail.com)."

__license__ = """This file is part of poliBeePsync.
poliBeePsync is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

poliBeePsync is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with poliBeePsync. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = 0.1

import filesettings
from requests import ConnectionError, Timeout
from appdirs import user_config_dir, user_data_dir
import os
import pickle
import sys
from polibeepsync.common import User, InvalidLoginError
import platform
import PySide
from PySide.QtCore import *
from PySide.QtGui import (QApplication, QMainWindow, QWidget,
                           QMenuBar, QMenu, QStatusBar, QAction,
                           QIcon, QFileDialog, QMessageBox, QFont,
                           QVBoxLayout, QLabel, QLineEdit, QSystemTrayIcon,
                            qApp, QDialog, QPixmap, QTextEdit, QTableView,
                            QTextCursor)

from ui_resizable import Ui_Form


class MySignal(QObject):
    sig = Signal(str)

class CoursesSignal(QObject):
    sig = Signal(list)

class LoginThread(QThread):
    def __init__(self, user, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal_ok = MySignal()
        self.signal_error = MySignal()
        self.user = user

    def run(self):
        while self.exiting==False:
            try:
                self.user.logout()
                self.user.login()
                if self.user.logged == True:
                    self.exiting=True
                    self.signal_ok.sig.emit('Successful login.')
            except IndexError:
                pass
                self.exiting = True
                self.signal_error.sig.emit('Already logged-in.')
                #frame.login_attempt.setText("You're already logged in.")
                #frame.myStream_message("You're already logged in.")
            except InvalidLoginError:
                self.user.logout()
                self.exiting = True
                self.signal_error.sig.emit('Login failed.')
                #frame.login_attempt.setText("Login failed.")
                #frame.myStream_message("Login failed.")
            except ConnectionError as err:
                self.user.logout()
                self.exiting = True
                self.signal_error.sig.emit('I can\'t connect to the server.'
                                 ' Is the Internet connection working?')
                #frame.login_attempt.setText("I can't connect to the server. Is the Internet connection working?")
                #frame.myStream_message(str(err) + "\nThis usually means that the Internet connection is not working.")
            except Timeout as err:
                self.user.logout()
                self.exiting = True
                self.signal_error.sig.emit("The timeout time has been reached."
                                 " Is the Internet connection working?")
                #frame.login_attempt.setText("The timeout time has been reached. Is the Internet connection working?")
                #frame.myStream_message(str(err) + "\nThis usually means that the Internet connection is not working.")
            except Exception as err:
                self.user.logout()
                self.exiting = True
                self.signal_error.sig.emit("An error occurred.")
                #frame.login_attempt.setText("An error occurred. See the *status* tab.")
                #frame.myStream_message(str(err))


class RefreshCoursesThread(QThread):
    def __init__(self, user, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.refreshed = MySignal()
        self.dumpuser = MySignal()
        self.newcourses = CoursesSignal()
        self.removable = CoursesSignal()
        self.user = user

    def run(self):
        while self.exiting==False:
            most_recent = self.user.get_online_courses()
            last = self.user.available_courses
            new = most_recent -last
            removable = last - most_recent
            if len(removable) >0:
                self.refreshed.sig.emit('The following courses have'
                                        ' been removed because they '
                      'aren\'t available online: {}'.format(removable))
            if len(new) > 0:
                for course in new:
                    course.save_folder_name = course.simplify_name(course.name)
                    self.refreshed.sig.emit('A new course '
                                            'was found: {}'.format(course))
            if len(new) == 0:
                self.refreshed.sig.emit('No new courses found.')
            self.user.sync_available_courses(most_recent)
            self.dumpuser.sig.emit('User object changed')
            self.newcourses.sig.emit(new)
            self.removable.sig.emit(removable)
            # nel main thread chaimare dumpUser()
            # e emettere segnale che passa new e removable

            #for course in new:
            #    self.courses_model.insertRows(0, 1, course)
            #for course in removable:
            #    index = self.courses_model.courses.index(course)
            #    self.courses_model.removeRows(index, 1)



class MyStream(QObject):
    message = Signal(str)
    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

    def flush(self):
        pass

class CoursesListModel(QAbstractTableModel):
    def __init__(self, courses):
        QAbstractTableModel.__init__(self)
        # il mio è un mapping, mentre con tableview viene più comodo avere indici
        self.courses = list(courses)

    def rowCount(self, parent=QModelIndex()):
        return len(self.courses)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def insertRows(self, position, rows, newcourse, parent= QModelIndex()):
        self.beginInsertRows(parent, position, position + rows -1)
        for row in range(rows):
            self.courses.insert(position, newcourse)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent = QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows -1)
        for row in range(rows):
            del self.courses[position]
        self.endRemoveRows()
        return True

    def flags(self, index):
        if index.column() == 2:
            flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            return flags
        elif index.column() == 1:
            flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable\
            | Qt.ItemIsUserCheckable
            return flags
        else: return Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if index.column() == 2:
                self.courses[index.row()].save_folder_name = value
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 1:
                self.courses[index.row()].sync = value
                self.dataChanged.emit(index, index)
                return True
        return False


    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.courses[index.row()].name
            if index.column() == 1:
                return self.courses[index.row()].sync
            if index.column() == 2:
                return self.courses[index.row()].save_folder_name
        elif role == Qt.CheckStateRole:
            return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0:
                return "Name"
            elif col == 1:
                return "Sync"
            elif col == 2:
                return "Save as"

class MainWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.appname = "poliBeePsync"
        self.settings_fname = 'pbs-settings.ini'
        self.data_fname = 'pbs.data'
        self.setupUi(self)
        self.w = QWidget()
        self.createTray()
        self.about.clicked.connect(self.about_box)
        self.license.clicked.connect(self.license_box)
        self.myStream = MyStream()
        self.myStream.message.connect(self.myStream_message)
        sys.stdout = self.myStream
        self.load_settings()
        self.load_data()

        self.loginthread = LoginThread(self.user)
        self.loginthread.terminated.connect(self.loginstatus)
        self.loginthread.signal_ok.sig.connect(self.loginstatus)

        self.refreshcoursesthread = RefreshCoursesThread(self.user)
        self.refreshcoursesthread.dumpuser.sig.connect(self.dumpUser)
        self.refreshcoursesthread.newcourses.sig.connect(self.addtocoursesview)
        self.refreshcoursesthread.removable.sig.connect(self.rmfromcoursesview)

        self.userCode.setText(str(self.user.username))
        self.userCode.textEdited.connect(self.setusercode)
        self.password.setText(self.user.password)
        self.password.textEdited.connect(self.setpassword)
        self.trylogin.clicked.connect(self.testlogin)

        self.courses_model = CoursesListModel(self.user.available_courses)
        self.coursesView.setModel(self.courses_model)
        self.refreshCourses.clicked.connect(self.refreshcourses)
        self.courses_model.dataChanged.connect(self.dumpUser)
        self.syncNow.clicked.connect(self.syncfiles)



        if self.settings['SyncNewCourses'] == str(True):
            self.sync_new = Qt.Checked
        else:
            self.sync_new = Qt.Unchecked

        if self.settings['NotifyNewCourses'] == str(True):
            self.notify_new = Qt.Checked
        else:
            self.notify_new = Qt.Unchecked

        self.rootfolder.setText(self.settings['RootFolder'])
        self.rootfolder.textChanged.connect(self.rootfolderslot)

        self.notifyNewCourses.setCheckState(self.notify_new)

        self.notifyNewCourses.stateChanged.connect(self.notifynew)

        self.addSyncNewCourses.setCheckState(self.sync_new)
        self.addSyncNewCourses.stateChanged.connect(self.syncnewslot)

        self.timerMinutes.setValue(int(self.settings['UpdateEvery']))
        self.timerMinutes.valueChanged.connect(self.updateminuteslot)

        self.changeRootFolder.clicked.connect(self.chooserootdir)


    def load_settings(self):
        for path in [user_config_dir(self.appname),
                     user_data_dir(self.appname)]:
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as err:
                if not os.path.isdir(path):
                    self.myStream_message(str(err))
        self.settings_path = os.path.join(user_config_dir(self.appname),
                                     self.settings_fname)
        self.settings = filesettings.settingsFromFile(self.settings_path)

    def load_data(self):
        try:
            with open(os.path.join(user_data_dir(self.appname),
                                   self.data_fname), 'rb') as f:
                self.user = pickle.load(f)
                print("Data has been loaded successfully.")
        except FileNotFoundError as err:
            self.user = User('', '')
            complete_message = str(err) + " ".join([
    "\nThis error means that no data can be found in the predefined",
    "directory. Ignore this if you're using poliBeePsync for "
    "the first time."])
            print(complete_message)
        except Exception as err:
            self.user = User('', '')
            print(str(err))

    def loginstatus(self, status):
        self.login_attempt.setText(status)

    @Slot(int)
    def notifynew(self, state):
        if state == 2:
            self.settings['NotifyNewCourses'] = 'True'
        else:
            self.settings['NotifyNewCourses'] = 'False'
        filesettings.settingsToFile(self.settings, self.settings_path)

    @Slot(int)
    def syncnewslot(self, state):
        if state == 2:
            self.settings['SyncNewCourses'] = 'True'
        else:
            self.settings['SyncNewCourses'] = 'False'
        filesettings.settingsToFile(self.settings, self.settings_path)

    @Slot(int)
    def updateminuteslot(self, minutes):
        self.settings['UpdateEvery'] = str(minutes)
        filesettings.settingsToFile(self.settings, self.settings_path)

    @Slot(str)
    def rootfolderslot(self, path):
        self.settings['RootFolder'] = path
        filesettings.settingsToFile(self.settings, self.settings_path)

    def chooserootdir(self):
        currentdir = self.settings['RootFolder']
        flags = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        newroot =  QFileDialog.getExistingDirectory(None,
            "Open Directory", currentdir, flags)
        if newroot != "":
            self.settings['RootFolder'] = str(newroot)
            filesettings.settingsToFile(self.settings, self.settings_path)
            self.rootfolder.setText(newroot)

    def setusercode(self):
        newcode = self.userCode.text()
        self.user.username = newcode
        try:
            self.dumpUser()
            print("User code changed to {}.".format(newcode))
        except Exception as err:
            print(str(err))


    def setpassword(self):
        newpass = self.password.text()
        self.user.password = newpass
        try:
            self.dumpUser()
            print("Password changed.")
        except Exception as err:
            print(str(err))

    def testlogin(self):
        if not self.loginthread.isRunning():
            self.loginthread.exiting = False
            self.loginthread.start()
            self.login_attempt.setStyleSheet("color: rgba(0, 0, 0, 255);")
            self.login_attempt.setText("Logging in, please wait.")

    def addtocoursesview(self, addlist):
        for elem in addlist:
            self.courses_model.insertRows(0, 1, elem)

    def rmfromcoursesview(self, removelist):
        for elem in removelist:
            index = self.courses_model.courses.index(elem)
            self.courses_model.removeRows(index, 1)


    def dumpUser(self):
        # we don't use the message...
        with open(os.path.join(user_data_dir(self.appname),
                               self.data_fname), 'wb') as f:
            pickle.dump(self.user, f)

    def refreshcourses(self):
        if not self.loginthread.isRunning():
            self.loginthread.exiting = False
            self.loginthread.start()
            self.loginthread.signal_ok.sig.connect(self.do_refreshcourses)

    def do_refreshcourses(self):
        if not self.refreshcoursesthread.isRunning():
            self.refreshcoursesthread.exiting = False
            self.refreshcoursesthread.start()

    def syncfiles(self):
        topdir = self.settings['RootFolder']

        for course in self.user.available_courses:
            subdir = course.save_folder_name
            if course.sync == True:
                outdir = os.path.join(topdir, subdir)
                os.makedirs(outdir, exist_ok=True)
                rootdir = self.user.find_files_and_folders(course.documents_url,
                                                      'root')
                self.user.save_files(rootdir, outdir)
            text = "Synced files for {}".format(course.name)
            print(text)

    @Slot(str)
    def myStream_message(self, message):
        self.status.moveCursor(QTextCursor.End)
        self.status.insertPlainText(message + "\n\n")

    def createTray(self):
        restoreAction = QAction("&Restore", self, triggered=self.showNormal)
        quitAction = QAction("&Quit", self, triggered=qApp.quit)
        icon =  PySide.QtGui.QIcon(':/newPrefix/polibeep.svg')
        trayIconMenu = QMenu()
        trayIconMenu.addAction(restoreAction)
        trayIconMenu.addAction(quitAction)
        trayIcon = QSystemTrayIcon(icon, self.w)
        trayIcon.setContextMenu(trayIconMenu)
        trayIcon.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def about_box(self):
        Dialog = QDialog()
        Dialog.setObjectName("Dialog")
        Dialog.resize(379, 161)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/newPrefix/polibeep-black.svg"), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        verticalLayout = QVBoxLayout(Dialog)
        verticalLayout.setObjectName("verticalLayout")
        label = QLabel(Dialog)
        label.setTextFormat(Qt.RichText)
        label.setOpenExternalLinks(True)
        label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        label.setScaledContents(True)
        label.setWordWrap(True)
        label.setObjectName("label")
        verticalLayout.addWidget(label)
        text = "<html><head/><body><p>poliBeePsync version {}.</p><p>poliBeePsync is a program written by Davide Olianas, released under GNU GPLv3+.</p><p><br/></p><p>More information is available on the <a href=\"http://www.davideolianas.com/polibeepsync\"><span style=\" text-decoration: underline; color:#0000ff;\">official website</span></a>.</p></body></html>".format(__version__)
        Dialog.setWindowTitle(QApplication.translate("Dialog", "About poliBeePsync", None, QApplication.UnicodeUTF8))
        label.setText(QApplication.translate("Dialog", text, None, QApplication.UnicodeUTF8))
        Dialog.exec_()

    def license_box(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        par = os.path.abspath(os.path.join(dir, os.pardir))
        lic = os.path.join(par, 'gpl.txt')
        with open(lic, 'rt') as f:
            text = f.read()
        Dialog = QDialog()
        Dialog.resize(600, 500)
        Dialog.setWindowTitle("License")
        layout = QVBoxLayout(Dialog)
        textEdit = QTextEdit(Dialog)
        layout.addWidget(textEdit)
        textEdit.setText(text)
        Dialog.exec_()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())
