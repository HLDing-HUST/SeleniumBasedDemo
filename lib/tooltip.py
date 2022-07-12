# coding:utf-8
from PyQt5.QtCore import QFile, QPropertyAnimation, QTimer, Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QHBoxLayout, QLabel)


class ToolTip(QFrame):

    def __init__(self, text='', ContentsMargins=(8, 6, 8, 6), font_size=10, position=(0, 0), direction=None,
                 parent=None):
        super().__init__(parent=parent)
        self.font_size = font_size
        self.position = position
        self.direction = direction
        self.__text = text
        self.__duration = 1000
        self.timer = QTimer(self)
        self.hBox = QHBoxLayout(self)
        self.label = QLabel(text, self)
        self.ani = QPropertyAnimation(self, b'windowOpacity', self)

        # set layout
        self.hBox.addWidget(self.label)
        # self.hBox.setContentsMargins(8, 6, 8, 6)
        # ContentsMargins:left,top,right,bottom
        self.hBox.setContentsMargins(ContentsMargins[0], ContentsMargins[1], ContentsMargins[2], ContentsMargins[3])

        # add shadow
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(32)
        self.shadowEffect.setColor(QColor(0, 0, 0, 60))
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        # set style
        self.setAttribute(Qt.WA_StyledBackground)
        self.setTheme('normal', False)
        self.__setQss()

    def text(self):
        return self.__text

    def setText(self, text: str):
        """ set text on tooltip """
        self.__text = text
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()

    def duration(self):
        return self.__duration

    def setDuration(self, duration: int):
        """ set tooltip duration in milliseconds """
        self.__duration = abs(duration)

    def __setQss(self):
        """ set style sheet """
        f = QFile("./lib/tooltip.qss")
        f.open(QFile.ReadOnly)
        qss_str = str(f.readAll(), encoding='utf-8')
        f.close()
        qss_str = qss_str.replace('10pt', str(self.font_size) + 'pt', 1)
        self.setStyleSheet(qss_str)

        self.label.adjustSize()
        self.adjustSize()

    def setTheme(self, status, dark=False):
        """ set dark theme """
        dark = 'true' if dark else 'false'
        self.setProperty('dark', dark)
        self.label.setProperty('dark', dark)
        self.label.setProperty('status', status)
        self.setStyle(QApplication.style())

    def setPosition(self):
        if self.direction is None:
            x = self.position[0]
            y = self.position[1]
            self.move(x, y)
        else:
            if self.direction == 'right':
                pos = self.parent().mapTo(self.parent(), QPoint(0, 0))  # 将小部件坐标pos转换为parent的坐标系
                # x = pos.x() + (self.width() - tip.width()) // 2
                x = pos.x() + self.parent().width() - self.width() - 3
                y = pos.y() + (self.parent().height() - self.height()) // 2

                # adjust postion to prevent tooltips from appearing outside the window
                x = min(max(0, x), self.parent().width())
                y = min(max(0, y), self.parent().height())
                self.move(x, y)

            if self.direction == 'left':
                pos = self.parent().mapTo(self.parent(), QPoint(0, 0))  # 将小部件坐标pos转换为parent的坐标系
                # x = pos.x() + (self.width() - tip.width()) // 2
                x = pos.x() + 3
                y = pos.y() + (self.parent().height() - self.height()) // 2

                # adjust postion to prevent tooltips from appearing outside the window
                x = min(max(0, x), self.parent().width())
                y = min(max(0, y), self.parent().height())
                self.move(x, y)

            if self.direction == 'top':
                pos = self.parent().mapTo(self.parent(), QPoint(0, 0))  # 将小部件坐标pos转换为parent的坐标系
                # x = pos.x() + (self.width() - tip.width()) // 2
                x = pos.x() + (self.parent().width() - self.width()) // 2
                y = pos.y() + 3

                # adjust postion to prevent tooltips from appearing outside the window
                x = min(max(0, x), self.parent().width())
                y = min(max(0, y), self.parent().height())
                self.move(x, y)

            if self.direction == 'bottom':
                pos = self.parent().mapTo(self.parent(), QPoint(0, 0))  # 将小部件坐标pos转换为parent的坐标系
                # x = pos.x() + (self.width() - tip.width()) // 2
                x = pos.x() + (self.parent().width() - self.width()) // 2
                y = pos.y() + self.parent().height() - self.height() - 3

                # adjust postion to prevent tooltips from appearing outside the window
                x = min(max(0, x), self.parent().width())
                y = min(max(0, y), self.parent().height())
                self.move(x, y)

            if self.direction == 'middle':
                pos = self.parent().mapTo(self.parent(), QPoint(0, 0))  # 将小部件坐标pos转换为parent的坐标系
                # x = pos.x() + (self.width() - tip.width()) // 2
                x = pos.x() + (self.parent().width() - self.width()) // 2
                y = pos.y() + (self.parent().height() - self.height()) // 2

                # adjust postion to prevent tooltips from appearing outside the window
                x = min(max(0, x), self.parent().width())
                y = min(max(0, y), self.parent().height())
                self.move(x, y)

    def show_tips(self, status='normal', theme=True, content="", time=1):
        self.setTheme(status, theme)
        self.setText(content)
        self.setDuration(time * 1000)
        self.hide()
        self.show()

    def show(self):
        self.setPosition()
        super(ToolTip, self).show()

    def showEvent(self, e):
        self.timer.stop()
        self.timer.setInterval(self.__duration)
        self.timer.start()
        super().showEvent(e)

    def hideEvent(self, e):
        self.timer.stop()
        super().hideEvent(e)
