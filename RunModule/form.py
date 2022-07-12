import csv
import math
import sys

from IPython.external.qt_for_kernel import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QCheckBox, QHeaderView, QStyle, \
    QStyleOptionButton, QTableWidgetItem, QDialogButtonBox, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QCoreApplication


class CheckBoxHeader(QHeaderView):
    """自定义表头类"""

    # 自定义 复选框全选信号
    select_all_clicked = pyqtSignal(bool)
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset = 0
    _y_offset = 0
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False
        self.all_header_combobox = []

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                    # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
                self.select_all_clicked.emit(self.isOn)

                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    # 自定义信号 select_all_clicked 的槽方法
    def change_state(self, isOn):
        # 如果行表头复选框为勾选状态
        if isOn:
            # 将所有的复选框都设为勾选状态
            for i in self.all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in self.all_header_combobox:
                i.setCheckState(Qt.Unchecked)


class TableDemo(QWidget):
    """窗口类"""
    trigger = pyqtSignal(bool)
    def __init__(self, data_path, parent=None):
        super(TableDemo, self).__init__(parent)
        self.data_path = data_path
        self.initUI()
        self.checkedList = []
        self.setTableContents()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def load_data(self):
        data = csv.reader(open(self.data_path, 'r', encoding='utf_8'))
        input = []
        for i in data:
            input.append([i])
        self.ColumnCount = len(i) + 1
        self.RowCount = len(input)
        self.header_field = ["全选"]
        self.data = input
        for j in range(self.ColumnCount):
            self.header_field.append("第{}列".format(j + 1))

    def initUI(self):
        self.setWindowTitle('选择自动化实例')
        self.load_data()
        self.resize(min(self.ColumnCount * 40 + 400, 900), min(self.RowCount * 20 + 200, 450))
        # 垂直布局
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setAlignment(Qt.AlignTop)  # 设置 垂直布局 的对齐方式
        self.setTableWidget()  # 设置表格
        # self.show()

    # 设置表格
    def setTableWidget(self):
        # 表格控件
        self.tablewidget = QTableWidget(self.RowCount, self.ColumnCount)  # 3行4列
        # self.tablewidget.setFixedWidth(300)         # 表格宽度
        self.setTableHeaderField()  # 设置表格行表头字段
        # self.tablewidget.setAlternatingRowColors(True)  # 交替行颜色
        self.vlayout.addWidget(self.tablewidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sure = QtWidgets.QPushButton()
        self.sure.setObjectName("sure")
        self.horizontalLayout.addWidget(self.sure)
        self.cancle = QtWidgets.QPushButton()
        self.cancle.setObjectName("cancle")
        self.horizontalLayout.addWidget(self.cancle)
        self.vlayout.addLayout(self.horizontalLayout)
        self.cancle.setText("取消")
        self.sure.setText("确定")
        self.cancle.clicked.connect(self.deleteLater)
        self.sure.clicked.connect(self.sure_event)
        # self.tablewidget.resizeColumnsToContents()
        self.tablewidget.resizeRowsToContents()
        self.tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)

    def sure_event(self):
        self.checkedList = []
        num = len(self.header.all_header_combobox)
        width = int(math.log10(num)) + 1
        for i, checkbox in enumerate(self.header.all_header_combobox):
            if checkbox.isChecked():
                index = str(i).rjust(width, '0')
                self.checkedList.append("::MyTestClass::test_rpa_"+index)
        self.trigger.emit(True)
        self.deleteLater()

    # 设置行表头字段
    def setTableHeaderField(self):
        self.header = CheckBoxHeader()
        for i in range(self.RowCount):
            checkbox = QCheckBox()
            # 将所有的复选框都添加到 全局变量 all_header_combobox 中
            self.header.all_header_combobox.append(checkbox)
            # 为每一行添加复选框
            self.tablewidget.setCellWidget(i, 0, checkbox)

            # 实例化自定义表头
        self.tablewidget.setHorizontalHeader(self.header)  # 设置表头
        self.tablewidget.setHorizontalHeaderLabels(self.header_field)  # 设置行表头字段
        self.tablewidget.setColumnWidth(0, 60)  # 设置第0列宽度
        self.header.select_all_clicked.connect(self.header.change_state)  # 行表头复选框单击信号与槽

    # 设置表格内容，根据实际情况设置即可
    def setTableContents(self):
        for i in range(self.RowCount):
            for j in range(self.ColumnCount - 1):
                self.tablewidget.setItem(i, j + 1, QTableWidgetItem(self.data[i][0][j]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ta = TableDemo('C:/Users/DHL/Desktop/rpa.csv')
    sys.exit(app.exec_())
