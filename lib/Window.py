import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import *

from lib.custom_grips import CustomGrip


class Window(QMainWindow):
    # function_list: [{'function': XXX,'name': XXX}]
    def __init__(self, window, function_list, resize=False):
        QMainWindow.__init__(self)
        self.window = window
        self.window_ui = window.ui
        self.function_list = function_list
        self.resize = resize
        # 按钮
        self.minimize_btn = None
        self.maxmize_btn = None
        self.close_btn = None
        for function in function_list:
            if function['function'] == 'minimize':
                self.minimize_btn = eval("self.window_ui." + function['name'])
                self.minimize_btn.clicked.connect(self.minimize_window)
            if function['function'] == 'maxmize':
                self.maxmize_btn = eval("self.window_ui." + function['name'])
                self.maxmize_btn.clicked.connect(self.maxmize_window)
            if function['function'] == 'close':
                self.close_btn = eval("self.window_ui." + function['name'])
                self.close_btn.clicked.connect(self.close_window)
        # 窗口标题绑定切换全屏和小窗
        if self.resize:
            self.window_ui.leftBox.mouseDoubleClickEvent = self.maxsize_or_restore
        # 拖动事件
        self.window_ui.titleRightInfo.mouseMoveEvent = self.moveWindow

        if self.resize:
            # 缩放
            # CUSTOM GRIPS
            self.left_grip = CustomGrip(self.window, Qt.LeftEdge, True)
            self.right_grip = CustomGrip(self.window, Qt.RightEdge, True)
            self.top_grip = CustomGrip(self.window, Qt.TopEdge, True)
            self.bottom_grip = CustomGrip(self.window, Qt.BottomEdge, True)

            # RESIZE WINDOW
            self.sizegrip = QSizeGrip(self.window_ui.frame_size_grip)
            self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")
        '''
        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.window_ui.bgApp.setGraphicsEffect(self.shadow)
        '''
        self.window_size = self.window.geometry()

    def maxsize_or_restore(self, event):
        self.maxmize_window()


    def moveWindow(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window.move(self.window.pos() + event.globalPos() - self.window.dragPos)
            self.window.dragPos = event.globalPos()
            event.accept()

    def maxmize_window(self):
        if self.window.isMaximized():
            self.window.showNormal()
            # self.window.resize(self.width() + 1, self.height()  + 1)
            # resize成最大化之前的窗口大小
            self.window.resize(self.window_size.width() + 1, self.window_size.height() + 1)
            self.window_ui.appMargins.setContentsMargins(10, 10, 10, 10)
            self.window_ui.maximizeRestoreAppBtn.setToolTip("最大化")
            self.window_ui.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/images/icons/icon_maximize.png"))
            # 窗口居中显示
            self.center()
            if self.resize:
                self.window_ui.frame_size_grip.show()
                self.left_grip.show()
                self.right_grip.show()
                self.top_grip.show()
                self.bottom_grip.show()
        else:
            self.window_size = self.window.geometry()
            self.window.showMaximized()
            self.window_ui.appMargins.setContentsMargins(0, 0, 0, 0)
            self.window_ui.maximizeRestoreAppBtn.setToolTip("恢复")
            self.window_ui.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/images/icons/icon_restore.png"))
            if self.resize:
                self.window_ui.frame_size_grip.hide()
                self.left_grip.hide()
                self.right_grip.hide()
                self.top_grip.hide()
                self.bottom_grip.hide()

    def center(self):
        # 获得屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获得窗口坐标系
        size = self.window.geometry()
        # 获得窗口相关坐标
        newLeft = (screen.width() - size.width()) // 2
        newTop = (screen.height() - size.height()) // 2
        # 移动窗口使其居中
        self.window.move(newLeft, newTop)

    def minimize_window(self):
        self.window.showMinimized()

    def close_window(self):
        # os._exit(0)
        self.window.close()

    def resize_grips(self):
        # 更改缩放边界值
        self.left_grip.setGeometry(0, 10, 10, self.window.height())
        self.right_grip.setGeometry(self.window.width() - 10, 10, 10, self.window.height())
        self.top_grip.setGeometry(0, 0, self.window.width(), 10)
        self.bottom_grip.setGeometry(0, self.window.height() - 10, self.window.width(), 10)
