import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from LoginModule.login_module import MainWindow as LoginUI
from MainWindowModule.main_window_module import MainWindow as MainWindowUI

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.LoginUI = LoginUI()
        self.MainWindowUI = MainWindowUI()
        self.LoginUI.login_signal.connect(self.login_success)
        self.MainWindowUI.logout_signal.connect(self.logout)

    def login_success(self, username):
        self.LoginUI.close()
        self.MainWindowUI.refresh_userinfo(username, self.LoginUI.login_cookies)
        self.MainWindowUI.show()

    def logout(self):
        self.MainWindowUI.close()
        self.MainWindowUI.destroy()
        self.MainWindowUI = MainWindowUI()
        self.MainWindowUI.logout_signal.connect(self.logout)
        self.LoginUI.toolTip.hide()
        self.LoginUI.show()

    def show(self):
        self.LoginUI.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("RPA.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
