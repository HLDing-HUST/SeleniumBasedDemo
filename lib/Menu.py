from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import os
from functools import partial

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class Menu(QMainWindow):
    # function_list: [{'btn_name': XXX,'page_name': XXX}]
    def __init__(self, window, btn_page_list):
        QMainWindow.__init__(self)
        self.window = window
        self.window_ui = window.ui
        self.btn_page_list = btn_page_list

        # 按钮
        # 隐藏/展开按钮
        self.toggleButton = self.window_ui.toggleButton
        self.toggleButton.clicked.connect(self.toggleMenu)
        self.fold_StyleSheet = "background-image: url(:/icons/images/icons/fold.svg);"
        self.unfold_StyleSheet = "background-image: url(:/icons/images/icons/unfold.png);"
        # 菜单按钮
        self.current_btn_index = 0
        self.menu_button_list = []
        for i in range(len(self.btn_page_list)):
            page_info = self.btn_page_list[i]
            btn = eval("self.window_ui." + page_info['btn_name'])
            # lambda 传参是传地址，所以在循环中不适用，应用partial
            btn.clicked.connect(partial(self.switch, i))
            self.menu_button_list.append(btn)

        # 点击后的样式qss
        self.MENU_SELECTED_STYLESHEET = """border-left: 22px solid 
        qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 
        rgba(109, 158, 235, 255), stop:0.5 rgba(85, 170, 255, 0));
        background-color: rgb(40, 44, 52);"""
        self.selectMenu(self.menu_button_list[self.current_btn_index])

        # menu宽度
        self.maxExtendWidth = 200
        self.standardWidth = 60
        # 动画
        self.animation_time = 0.5 * 1000
        self.animation = QPropertyAnimation(self.window_ui.leftMenuBg, b"minimumWidth")
        # 隐藏菜单
        self.window_ui.textEdit.setMinimumSize(self.maxExtendWidth-18, 0)
        self.window_ui.toggleLeftBox.clicked.connect(self.toggleLeftBox)
        self.window_ui.extraCloseColumnBtn.clicked.connect(self.toggleLeftBox)
        self.window_ui.userinfoBtn.clicked.connect(self.toggleRightBox)

    def toggleMenu(self):
        width = self.window_ui.leftMenuBg.width()
        if width == self.standardWidth:
            widthExtended = self.maxExtendWidth
        else:
            widthExtended = self.standardWidth

        # 设置动画
        self.animation.stop()
        self.animation.setDuration(self.animation_time)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        if width == self.standardWidth:
            # 更改按钮图标
            self.window_ui.toggleButton.setStyleSheet(self.fold_StyleSheet)
        else:
            # 更改按钮图标
            self.window_ui.toggleButton.setStyleSheet(self.unfold_StyleSheet)

    def switch(self, index):
        self.deselectMenu(self.menu_button_list[self.current_btn_index])
        self.current_btn_index = index
        self.selectMenu(self.menu_button_list[self.current_btn_index])
        self.window_ui.stackedWidget.setCurrentIndex(self.current_btn_index)

    # SELECT
    def selectMenu(self, btn):
        getStyle = btn.styleSheet()
        select = getStyle + self.MENU_SELECTED_STYLESHEET
        btn.setStyleSheet(select)

    # DESELECT
    def deselectMenu(self, btn):
        getStyle = btn.styleSheet()
        deselect = getStyle.replace(self.MENU_SELECTED_STYLESHEET, "")
        btn.setStyleSheet(deselect)

    # TOGGLE LEFT BOX
    # ///////////////////////////////////////////////////////////////
    def toggleLeftBox(self):
        # GET WIDTH
        width = self.window_ui.extraLeftBox.width()
        widthRightBox = self.window_ui.extraRightBox.width()
        self.start_box_animation(width, widthRightBox, "left")

    # TOGGLE RIGHT BOX
    # ///////////////////////////////////////////////////////////////
    def toggleRightBox(self):
        # GET WIDTH
        width = self.window_ui.extraRightBox.width()
        widthLeftBox = self.window_ui.extraLeftBox.width()
        self.start_box_animation(widthLeftBox, width, "right")

    def start_box_animation(self, left_box_width, right_box_width, direction):
        # Check values
        if left_box_width == 0 and direction == "left":
            left_width = self.maxExtendWidth
        else:
            left_width = 0
        # Check values
        if right_box_width == 0 and direction == "right":
            right_width = self.maxExtendWidth
        else:
            right_width = 0

        # ANIMATION LEFT BOX
        self.left_box = QPropertyAnimation(self.window_ui.extraLeftBox, b"minimumWidth")
        self.left_box.setDuration(self.animation_time)
        self.left_box.setStartValue(left_box_width)
        self.left_box.setEndValue(left_width)
        self.left_box.setEasingCurve(QEasingCurve.InOutQuart)

        # ANIMATION RIGHT BOX
        self.right_box = QPropertyAnimation(self.window_ui.extraRightBox, b"minimumWidth")
        self.right_box.setDuration(self.animation_time)
        self.right_box.setStartValue(right_box_width)
        self.right_box.setEndValue(right_width)
        self.right_box.setEasingCurve(QEasingCurve.InOutQuart)

        # GROUP ANIMATION
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(self.left_box)
        self.group.addAnimation(self.right_box)
        self.group.start()
