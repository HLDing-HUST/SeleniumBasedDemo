from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from lib.Window import Window
from lib.Menu import Menu
from .mainWindow import Ui_MainWindow as mainWindow_ui
from ExampleModule.example_moudle import MainWindow as example_ui
from InstructModule.instruct_module import MainWindow as instruct_ui
from RunModule.run_moudle import MainWindow as run_ui
os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):
    # 定义登出信号
    logout_signal = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = mainWindow_ui()
        self.ui.setupUi(self)

        self.page_list = [{'page_ui': 'instruct_ui', 'btn_name': 'btn_instruct'},
                          {'page_ui': 'run_ui', 'btn_name': 'btn_run'}]

        for i in range(len(self.page_list)):
            ui = eval(self.page_list[i]['page_ui'] + '()')
            index = self.ui.stackedWidget.addWidget(ui)
            self.page_list[i].update({'page_index': index})
        self.ui.stackedWidget.setCurrentIndex(0)

        self.Menu = Menu(self, self.page_list)
        self.cookies = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        Window_function_list = [{'function': 'minimize', 'name': 'minimizeAppBtn'},
                                {'function': 'maxmize', 'name': 'maximizeRestoreAppBtn'},
                                {'function': 'close', 'name': 'closeAppBtn'}]
        self.Window = Window(self, Window_function_list, resize=True)
        self.init_slot_function()

    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        self.Window.resize_grips()

    def init_slot_function(self):
        self.ui.btn_logout.clicked.connect(self.logout)

    def refresh_userinfo(self, username, cookies):
        username_refine = ' ' * 2 + username
        width = 20 + len(username_refine) * 8
        self.ui.userinfoBtn.setMinimumSize(width, 0)
        self.ui.userinfoBtn.setText(username_refine)
        self.cookies = cookies

    def logout(self):
        self.cookies = None
        self.logout_signal.emit()
