from PyQt5.QtCore import Qt, QPoint, QRegExp
from PyQt5.QtGui import QIcon, QValidator, QRegExpValidator
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout
from PyQt5 import QtCore, QtWidgets

from lib.tooltip import ToolTip


# 重写LineEdit类，加入清除按钮，添加输入正则，添加提示功能
class MyLineEdit(QLineEdit):
    def __init__(self, name, PlaceholderText, width, EchoMode, Rule, input_tips, parent=None):
        super(QLineEdit, self).__init__(parent)
        # 清除按钮
        self.btn = QPushButton(QIcon(":/icons/images/icons/icon_close.png"), "", self)
        self.btn.setStyleSheet("QPushButton {border-radius: 12px;} "
                               "QPushButton:hover {border: 2px solid rgb(90, 100, 120);}"
                               "QPushButton:pressed {border: 3px solid rgb(60, 70, 90);}")
        self.btn.setFixedSize(25, 25)
        self.btn.hide()
        self.btn.setObjectName(self.objectName() + "_clear_btn")
        self.btn.clicked.connect(self.clear_text)
        self.btn.setFocusPolicy(Qt.NoFocus)  # 必须设置成无焦点，否则会在点击的时候让输入框失去焦点，转移到下一个输入框
        # 添加布局，使按钮靠右
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self.btn)
        self.setLayout(layout)
        # 设置LineEdit相关属性
        self.setPlaceholderText(PlaceholderText)
        self.setMinimumSize(QtCore.QSize(0, width))
        self.setMaximumSize(QtCore.QSize(16777215, width))
        self.setInputMask("")
        self.setText("")
        self.setMaxLength(20)
        self.setEchoMode(eval('QtWidgets.QLineEdit.' + EchoMode))
        # 如果是Password就禁止中文输入
        if EchoMode == 'Password':
            self.setAttribute(Qt.WA_InputMethodEnabled, False)
        else:
            self.setAttribute(Qt.WA_InputMethodEnabled, True)
        # 设置正则规范
        self.setValidator(MyQRegExpValidator(QRegExp(Rule), self.show_tooltip, input_tips))
        self.setCursorPosition(0)
        self.setObjectName(name)
        self.textEdited.connect(self.finish_edit)
        # 添加提示
        self.toolTip = ToolTip(direction='right', parent=self)
        self.toolTip.setTheme('normal', True)
        self.toolTip.hide()

    def focusInEvent(self, e):
        if len(self.text()) > 0:
            self.btn.show()
        super(MyLineEdit, self).focusInEvent(e)

    def focusOutEvent(self, e):
        super(MyLineEdit, self).focusOutEvent(e)

    def clear_text(self):
        self.setText("")
        self.btn.hide()

    def finish_edit(self):
        if len(self.text()) > 0:
            self.btn.show()
        else:
            self.btn.hide()

    def show_tooltip(self, tips, status, time):
        self.toolTip.show_tips(status, True, tips, time)

    def hide_tooltip(self):
        self.toolTip.hide()


# 重写正则函数类，加入提示
class MyQRegExpValidator(QRegExpValidator):
    def __init__(self, QRegExp, tips, content, parent=None):
        super(MyQRegExpValidator, self).__init__(QRegExp, parent)
        self.tips = tips  # 提示函数
        self.content = content

    def validate(self, p_str, p_int):  # real signature unknown; restored from __doc__
        """ validate(self, str, int) -> Tuple[QValidator.State, str, int] """
        result = super(MyQRegExpValidator, self).validate(p_str, p_int)
        if result[0] == 0:  # 为0代表输入不符合规范
            self.tips(self.content, 'warning', 1)
        return result
