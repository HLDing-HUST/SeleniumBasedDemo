import base64
import json
import os
import sys

import rsa
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from RunModule.encode import rsa_encrypt_bytes, rsa_decrypt
from .OCR_PRA import Ui_MainWindow
from WebModule.MyBrowser import MyBrowser

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.my_browser = MyBrowser()
        self.my_browser_show()
        self.instruct_list = self.ui.instruct_list
        self.instruct_num = 0
        self.instruct_order_list = []
        self.instruct_info_list = []
        self.login_order_list = ['打开登录网址', '用户名', '密码', '验证码', '验证码图片', '登录按钮']
        self.login_info_list = [{'name': '打开登录网址', 'info': {'type': 0, 'xpath': '', 'index': '0'}},
                                {'name': '用户名', 'info': {'type': 2, 'xpath': '', 'index': '0', 'extra_input': ''}},
                                {'name': '密码', 'info': {'type': 2, 'xpath': '', 'index': '0', 'extra_input': ''}},
                                {'name': '验证码', 'info': {'type': 2, 'xpath': '', 'index': '0'}},
                                {'name': '验证码图片', 'info': {'type': 5, 'xpath': '', 'index': '0'}},
                                {'name': '登录按钮', 'info': {'type': 1, 'xpath': '', 'index': '0'}}]
        # self.table_editor = self.ui.table_editor
        # self.table_editor.setEnabled(False)
        self.show_extra_input(False)
        self.xpath_table = self.ui.xpath_table
        self.connect_slot()

    def my_browser_show(self):
        self.ui.borswer_layout.addWidget(self.my_browser)
        self.my_browser.show()

    def connect_slot(self):
        self.ui.add_row.clicked.connect(self.add_rows)
        self.ui.delete_row.clicked.connect(self.delete_rows)
        self.ui.type.currentIndexChanged.connect(self.change_type)
        self.ui.submit.clicked.connect(self.submit)
        self.ui.clear.clicked.connect(self.clear_input)
        self.instruct_list.itemSelectionChanged.connect(self.click_instruct_list)
        self.instruct_list.clicked.connect(self.click_instruct_list)
        self.instruct_list.doubleClicked.connect(self.double_click_instruct_list)
        self.ui.edit_instruct.clicked.connect(self.double_click_instruct_list)
        self.ui.add_instruct.clicked.connect(self.add_instruct)
        self.ui.delete_instruct.clicked.connect(self.delete_instruct)
        self.ui.up_instruct.clicked.connect(self.up_instruct)
        self.ui.down_instruct.clicked.connect(self.down_instruct)
        self.ui.show_instruct.clicked.connect(self.show_instruct)
        self.ui.save_instruct.clicked.connect(self.save_file)
        self.ui.open_instruct.clicked.connect(self.load_file)
        self.ui.clear_instruct.clicked.connect(self.clear_all)

    def clear_all(self):
        flag = False
        for info in self.login_info_list:
            if len(info['info']['xpath']) > 0:
                flag = True
                break
        if len(self.instruct_order_list) > 0:
            flag = True
        if flag:  # 当前界面有指令
            event = QMessageBox.information(self, '是否保存', '当前界面存在指令，是否保存？',
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                            QMessageBox.Yes)
            if event == QMessageBox.Yes:
                self.save_file()
            elif event == QMessageBox.Cancel:
                return
        self.clear_input()
        self.show_extra_input(False)
        self.ui.extra_input.setText('')
        self.change_input_status(False)
        self.change_table_status(False)
        self.instruct_num = 0
        self.instruct_order_list = []
        self.instruct_info_list = []
        self.login_order_list = ['打开登录网址', '用户名', '密码', '验证码', '验证码图片', '登录按钮']
        self.login_info_list = [{'name': '打开登录网址', 'info': {'type': 0, 'xpath': '', 'index': '0'}},
                                {'name': '用户名', 'info': {'type': 2, 'xpath': '', 'index': '0', 'extra_input': ''}},
                                {'name': '密码', 'info': {'type': 2, 'xpath': '', 'index': '0', 'extra_input': ''}},
                                {'name': '验证码', 'info': {'type': 2, 'xpath': '', 'index': '0'}},
                                {'name': '验证码图片', 'info': {'type': 5, 'xpath': '', 'index': '0'}},
                                {'name': '登录按钮', 'info': {'type': 1, 'xpath': '', 'index': '0'}}]
        self.reload_instruct_list()
        login_operation = self.instruct_list.findItems('登录', QtCore.Qt.MatchContains, column=0)[0]
        self.instruct_list.setCurrentItem(login_operation)
        self.ui.edit_dockwidget.setWindowTitle('登录')

    def change_type(self, type_index):
        if type_index < 4 or type_index == 5:  # 为 打开网址、点击、输入文本、切换、获取元素
            self.change_table_status(False)
        else:
            self.change_table_status(True)
        if type_index < 2 or type_index == 5:
            self.ui.index.setEnabled(False)
            self.ui.index_label.setEnabled(False)
        else:  # 为 输入文本、切换、复选
            self.ui.index.setEnabled(True)
            self.ui.index_label.setEnabled(True)

    def show_extra_input(self, status=False, lable=''):
        self.ui.extra_input.setVisible(status)
        self.ui.extra_label.setVisible(status)
        self.ui.extra_label.setText(lable)
        self.ui.extra_label.setEnabled(status)
        self.ui.extra_input.setEnabled(status)

        self.ui.index.setVisible(not status)
        self.ui.index_label.setVisible(not status)

    def add_type_item(self, status=False):
        if status:
            if self.ui.type.count() == 5:
                self.ui.type.addItem('获取元素')
        else:
            if self.ui.type.count() == 6:
                self.ui.type.removeItem(5)

    def add_rows(self):
        row_num = self.xpath_table.currentRow()
        if row_num < 0:
            row_num = self.xpath_table.rowCount() - 1  # 获取当前的列数
        # self.xpath_table.setRowCount(row_num + 1)  # 添加一行
        self.xpath_table.insertRow(row_num + 1)  # 添加一行

    def delete_rows(self):
        row_num = self.xpath_table.currentRow()  # 获取当前选中的行
        if row_num < 0:
            row_num = self.xpath_table.rowCount() - 1
        self.xpath_table.removeRow(row_num)  # 删除指定行

    def submit(self):
        result, information = self.get_result()
        type_index = result['type']
        xpath = result['xpath']
        if len(xpath) == 0:
            QMessageBox.critical(self, '错误', '定位方式为空，请填写完整再提交！', QMessageBox.Yes)
            return 0
        if 'extra_input' in result.keys():
            extra_input = result['extra_input']
            if len(extra_input) == 0:
                path = self.ui.edit_dockwidget.windowTitle().split('\\', 1)
                if len(path) > 1:
                    name = path[1]
                    if name == '用户名':
                        QMessageBox.critical(self, '错误', '用户名为空，请填写完整再提交！', QMessageBox.Yes)
                    elif name == '密码':
                        QMessageBox.critical(self, '错误', '密码为空，请填写完整再提交！', QMessageBox.Yes)
                    return 0
        if type_index >= 4 and type_index != 5:
            value_table = result['value_table']
            if len(value_table) == 0:
                QMessageBox.critical(self, '错误', 'XPath表格为空，请填写完整再提交！', QMessageBox.Yes)
                return 0
        event = QMessageBox.information(self, '核对', information, QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
        if event == QMessageBox.Yes:
            # self.clear_input()
            # print(result)
            self.refresh_instruct_info(result)
            return 1
        return 0

    def get_result(self):
        type_dict = {'0': '获取元素', '1': '打开网址', '2': '点击', '3': '输入文本', '4': '单选', '5': '多选'}
        result = {}
        information = '请核查所填写的内容是否正确\n'
        type_index = self.ui.type.currentIndex()
        information += '操作名称：' + self.ui.edit_dockwidget.windowTitle().split('\\', 1)[1] + '\n'
        information += '操作类型：' + type_dict[str(type_index)] + '\n'
        result.update({'type': type_index})
        xpath = ''
        index = 0
        value_table = []
        if type_index < 4 or type_index == 5:  # 为打开网址、点击、输入文本
            xpath = self.ui.xpath.text()
            index = self.ui.index.text()
            if self.ui.extra_input.isEnabled():
                extra_input = self.ui.extra_input.text()
                result.update({'extra_input': extra_input})
                path = self.ui.edit_dockwidget.windowTitle().split('\\', 1)
                if len(path) > 1:
                    name = path[1]
                    if name == '用户名':
                        information += '用户名：' + extra_input + '\n'
                    elif name == '密码':
                        information += '密码：' + extra_input + '\n'
            # print(xpath, index)
            '''
            if len(xpath) == 0:
                QMessageBox.critical(self, '错误', '定位方式为空，请填写完整再提交！', QMessageBox.Yes)
                return
            '''
            result.update({'xpath': xpath})
            result.update({'index': index})
            information += '定位方式：' + xpath + '\n'
            if type_index == 5:
                information += '数据索引：' + index + '\n'
        else:
            xpath = self.ui.xpath.text()
            index = self.ui.index.text()
            for i in range(self.xpath_table.rowCount()):
                if self.xpath_table.item(i, 0) is not None and self.xpath_table.item(i, 1) is not None:
                    value_table.append([self.xpath_table.item(i, 0).text(), self.xpath_table.item(i, 1).text()])
            # print(xpath, index, value_table)
            '''
            if len(xpath) == 0 or len(value_table) == 0:
                if len(xpath) == 0:
                    QMessageBox.critical(self, '错误', '定位方式为空，请填写完整再提交！', QMessageBox.Yes)
                if len(value_table) == 0:
                    QMessageBox.critical(self, '错误', 'XPath表格为空，请填写完整再提交！', QMessageBox.Yes)
                return
            '''
            result.update({'xpath': xpath})
            result.update({'index': index})
            result.update({'value_table': value_table})
            information += '定位方式：' + xpath + '\n'
            information += '数据索引：' + index + '\n'
            information += 'XPath表格：' + '\n'
            space_num = len('XPath表格：')
            for i in range(len(value_table)):
                information += space_num * ' ' + 'name：' + value_table[i][0] + ' ' * 4
                information += 'XPath：' + value_table[i][1] + '\n'
        return result, information

    def clear_input(self):
        self.ui.type.setCurrentIndex(0)
        self.ui.xpath.clear()
        self.ui.index.setValue(0)
        self.xpath_table.clearContents()
        self.xpath_table.setRowCount(1)

    def click_instruct_list(self):
        item = self.instruct_list.currentItem()
        # print(item.parent().text(0))
        ret = self.getLocation(item)  # 获取选中节点父节点
        if ret:
            bin_path = os.path.join(ret, item.text(0))
        else:
            bin_path = os.path.join(item.text(0))
        bin_path_list = bin_path.split('\\', 1)
        if len(bin_path_list) == 1:
            self.ui.up_instruct.setEnabled(False)
            self.ui.down_instruct.setEnabled(False)
            self.ui.delete_instruct.setEnabled(False)
            self.ui.edit_instruct.setEnabled(False)
            # self.ui.edit_dockwidget.setEnabled(False)
            self.ui.show_instruct.setEnabled(False)
            if bin_path_list[0] == '登录':
                self.ui.add_instruct.setEnabled(False)
            else:
                self.ui.add_instruct.setEnabled(True)
        else:
            if bin_path_list[0] == '登录':
                self.ui.up_instruct.setEnabled(False)
                self.ui.down_instruct.setEnabled(False)
                self.ui.delete_instruct.setEnabled(False)
                self.ui.edit_instruct.setEnabled(True)
                self.ui.add_instruct.setEnabled(False)
                self.ui.show_instruct.setEnabled(True)
            else:
                self.ui.up_instruct.setEnabled(True)
                self.ui.down_instruct.setEnabled(True)
                self.ui.delete_instruct.setEnabled(True)
                self.ui.edit_instruct.setEnabled(True)
                self.ui.add_instruct.setEnabled(True)
                self.ui.show_instruct.setEnabled(True)

    def double_click_instruct_list(self):
        # instruct_name_list = ['用户名','密码','验证码','验证码图片','登录按钮']
        item = self.instruct_list.currentItem()
        # print(item.parent().text(0))
        ret = self.getLocation(item)  # 获取选中节点父节点
        if ret:
            bin_path = os.path.join(ret, item.text(0))
        else:
            bin_path = os.path.join(item.text(0))

        path = self.ui.edit_dockwidget.windowTitle().split('\\', 1)
        if len(path) > 1:
            parent = path[0]
            name = path[1]
            if parent == '登录':
                index = self.login_order_list.index(name)
                # 如果指令中有内容
                result, information = self.get_result()
                # print(result, self.login_info_list[index]['info'])
                if result != self.login_info_list[index]['info']:
                    event = QMessageBox.information(self, '是否保存', '[' + name + ']更改未保存，是否保存？',
                                                    QMessageBox.Yes | QMessageBox.No,
                                                    QMessageBox.Yes)
                    if event == QMessageBox.Yes:
                        result = self.submit()
                        if result == 0:
                            return

            else:
                index = self.instruct_order_list.index(name)
                # 如果指令中有内容
                result, information = self.get_result()
                # print(result, self.instruct_info_list[index]['info'])
                if result != self.instruct_info_list[index]['info']:
                    event = QMessageBox.information(self, '是否保存', '[' + name + ']更改未保存，是否保存？',
                                                    QMessageBox.Yes | QMessageBox.No,
                                                    QMessageBox.Yes)
                    if event == QMessageBox.Yes:
                        result = self.submit()
                        if result == 0:
                            return

        self.ui.edit_dockwidget.setWindowTitle(bin_path)
        bin_path_list = bin_path.split('\\', 1)
        self.clear_input()
        self.show_in_edit(bin_path_list)
        self.show_extra_input(False)
        if bin_path_list[0] == '登录':  # 登录指令
            if item.text(0) == '打开登录网址':
                self.change_type_and_index(type=0, index=False)
            elif item.text(0) == '用户名':
                self.show_extra_input(True, '用户名')
                self.change_type_and_index(type=2, index=False)
            elif item.text(0) == '密码':
                self.show_extra_input(True, '密码')
                self.change_type_and_index(type=2, index=False)
            elif item.text(0) == '验证码':
                self.change_type_and_index(type=2, index=False)
            elif item.text(0) == '验证码图片':
                self.change_type_and_index(type=5, index=False)
            elif item.text(0) == '登录按钮':
                self.change_type_and_index(type=1, index=False)
            else:
                self.change_input_status(False)
        else:
            if len(bin_path_list) > 1:
                # self.ui.edit_dockwidget.setEnabled(True)
                # self.ui.edit_dockWidgetContent.setEnabled(True)
                self.change_table_status(False)
                self.change_input_status(True)
                self.change_type(self.ui.type.currentIndex())
            else:
                self.change_input_status(False)
                self.change_table_status(False)

    def show_in_edit(self, bin_path_list):
        if len(bin_path_list) > 1:
            if bin_path_list[0] == '登录':
                self.add_type_item(True)
                index = self.login_order_list.index(bin_path_list[1])
                if len(self.login_info_list[index]['info'].keys()) > 0:
                    info = self.login_info_list[index]['info']
                    self.ui.type.setCurrentIndex(int(info['type']))
                    self.ui.xpath.setText(info['xpath'])
                    self.ui.extra_input.setText('')
                    if 'extra_input' in info.keys():
                        self.ui.extra_input.setText(info['extra_input'])
                    if int(info['type']) < 4 or info['type'] == 5:
                        if int(info['type']) == 2 or int(info['type']) == 3:
                            self.ui.index.setValue(int(info['index']))
                        else:
                            self.ui.index.setValue(0)
                            self.ui.index.setEnabled(False)
                    else:
                        self.ui.index.setValue(int(info['index']))
                        self.ui.xpath_table.setRowCount(len(info['value_table']))
                        for i in range(len(info['value_table'])):
                            newItem = QTableWidgetItem(info['value_table'][i][0])
                            self.ui.xpath_table.setItem(i, 0, newItem)
                            newItem = QTableWidgetItem(info['value_table'][i][1])
                            self.ui.xpath_table.setItem(i, 1, newItem)
            else:
                self.add_type_item(False)
                index = self.instruct_order_list.index(bin_path_list[1])
                if len(self.instruct_info_list[index]['info'].keys()) > 0:
                    info = self.instruct_info_list[index]['info']
                    self.ui.type.setCurrentIndex(int(info['type']))
                    self.ui.xpath.setText(info['xpath'])
                    if int(info['type']) < 4:
                        if int(info['type']) == 2 or int(info['type']) == 3:
                            self.ui.index.setValue(int(info['index']))
                        else:
                            self.ui.index.setValue(0)
                            self.ui.index.setEnabled(False)
                    else:
                        self.ui.index.setValue(int(info['index']))
                        self.ui.xpath_table.setRowCount(len(info['value_table']))
                        for i in range(len(info['value_table'])):
                            newItem = QTableWidgetItem(info['value_table'][i][0])
                            self.ui.xpath_table.setItem(i, 0, newItem)
                            newItem = QTableWidgetItem(info['value_table'][i][1])
                            self.ui.xpath_table.setItem(i, 1, newItem)
        else:
            self.ui.type.setCurrentIndex(0)
            self.ui.xpath.setText('')
            self.ui.index.setValue(0)
            self.ui.index.setValue(0)
            self.ui.index.setEnabled(False)

    def change_input_status(self, status):
        self.ui.submit.setEnabled(status)
        self.ui.clear.setEnabled(status)
        self.ui.type.setEnabled(status)
        self.ui.type_label.setEnabled(status)
        self.ui.index.setEnabled(False)
        self.ui.index_label.setEnabled(False)
        self.ui.xpath.setEnabled(status)
        self.ui.xpath_label.setEnabled(status)

    def change_table_status(self, status):
        self.ui.add_row.setEnabled(status)
        self.ui.delete_row.setEnabled(status)
        self.ui.xpath_table.setEnabled(status)

    def change_type_and_index(self, type=0, index=False):
        # self.ui.edit_dockwidget.setEnabled(True)
        # self.ui.edit_dockWidgetContent.setEnabled(True)
        self.ui.submit.setEnabled(True)
        self.ui.clear.setEnabled(True)

        self.ui.type.setCurrentIndex(type)
        self.ui.type.setEnabled(False)
        self.ui.type_label.setEnabled(True)
        self.ui.index.setEnabled(index)
        self.ui.index_label.setEnabled(index)
        self.ui.xpath.setEnabled(True)
        self.ui.xpath_label.setEnabled(True)

    def getLocation(self, item):
        if item.parent():
            temp = item.parent().text(0)
            parent = self.getLocation(item.parent())  # 递归获取上层节点，直到顶层
            if parent:
                res = os.path.join(parent, temp)
                return res
            else:
                return temp  # 最终返回节点索引
        else:
            return 0

    def add_instruct(self):
        item = self.instruct_list.currentItem()
        # print(item.parent().text(0))
        ret = self.getLocation(item)  # 获取选中节点父节点
        if ret:
            bin_path = os.path.join(ret, item.text(0))
        else:
            bin_path = os.path.join(item.text(0))
        bin_path_list = bin_path.split('\\', 1)
        self.instruct_num += 1
        name, ok = QInputDialog.getText(self, "输入操作名称", "请输入操作名称\n\n请输入文本:", QLineEdit.Normal, "")
        if not ok:
            return
        name = '操作' + str(self.instruct_num) + '-' + name
        if len(bin_path_list) == 1:
            if bin_path_list[0] == '操作':
                child = QTreeWidgetItem(self.instruct_list.currentItem())
                child.setText(0, name)
                self.instruct_order_list.append(name)
                self.instruct_info_list.append({'name': name, 'info': {'type': 0, 'xpath': '', 'index': '0'}})
                self.instruct_list.expandItem(self.instruct_list.currentItem())
        else:
            # index1 = item.parent().indexOfChild(item)
            child = QTreeWidgetItem(self.instruct_list.currentItem().parent())
            child.setText(0, name)
            self.instruct_order_list.append(name)
            self.instruct_info_list.append({'name': name, 'info': {'type': 0, 'xpath': '', 'index': '0'}})
            self.instruct_list.expandItem(self.instruct_list.currentItem().parent())
            '''
            index2 = item.parent().childCount() - 1
            self.instruct_order_list.append(name)
            self.instruct_info_list.append({'name': name, 'info': {}})
            self.instruct_order_list[index1 + 1], self.instruct_order_list[index2] = self.instruct_order_list[index2], \
                                                                                     self.instruct_order_list[
                                                                                         index1 + 1]
            self.instruct_info_list[index1 + 1], self.instruct_info_list[index2] = self.instruct_info_list[index2], \
                                                                                   self.instruct_info_list[index1 + 1]
            for i in range(index1+1, item.parent().childCount()):
                name1 = item.parent().child(i).text(0)
                name2 = item.parent().child(item.parent().childCount()-1).text(0)
                item.parent().child(i).setText(0, name2)
                item.parent().child(item.parent().childCount()-1).setText(0, name1)
            '''
        # print(self.instruct_order_list, self.instruct_info_list)

    def delete_instruct(self):
        item = self.instruct_list.currentItem()
        self.instruct_list.currentItem().parent().removeChild(item)
        index = self.instruct_order_list.index(item.text(0))
        name = item.text(0)
        bin_path_list = self.ui.edit_dockwidget.windowTitle().split('\\', 1)
        if name in bin_path_list:
            self.clear_input()
            self.ui.edit_dockwidget.setWindowTitle('')
        self.instruct_order_list.pop(index)
        self.instruct_info_list.pop(index)
        # print(self.instruct_order_list, self.instruct_info_list)

    def up_instruct(self):
        item = self.instruct_list.currentItem()
        index = self.instruct_order_list.index(item.text(0))
        if index > 0:
            self.instruct_order_list[index - 1], self.instruct_order_list[index] = self.instruct_order_list[index], \
                                                                                   self.instruct_order_list[index - 1]
            self.instruct_info_list[index - 1], self.instruct_info_list[index] = self.instruct_info_list[index], \
                                                                                 self.instruct_info_list[index - 1]
            # print(self.instruct_order_list, self.instruct_info_list)
            self.refresh_instruct_list(index - 1, index)
            self.instruct_list.setCurrentItem(item.parent().child(index - 1))

    def down_instruct(self):
        item = self.instruct_list.currentItem()
        index = self.instruct_order_list.index(item.text(0))
        if index < len(self.instruct_order_list) - 1:
            self.instruct_order_list[index], self.instruct_order_list[index + 1] = self.instruct_order_list[index + 1], \
                                                                                   self.instruct_order_list[index]
            self.instruct_info_list[index], self.instruct_info_list[index + 1] = self.instruct_info_list[index + 1], \
                                                                                 self.instruct_info_list[index]
            # print(self.instruct_order_list, self.instruct_info_list)
            self.refresh_instruct_list(index, index + 1)
            self.instruct_list.setCurrentItem(item.parent().child(index + 1))

    def refresh_instruct_list(self, index1, index2):
        parent = self.instruct_list.currentItem().parent()
        name1 = parent.child(index1).text(0)
        name2 = parent.child(index2).text(0)
        parent.child(index1).setText(0, name2)
        parent.child(index2).setText(0, name1)

    def refresh_instruct_info(self, result):
        parent = self.ui.edit_dockwidget.windowTitle().split('\\', 1)[0]
        name = self.ui.edit_dockwidget.windowTitle().split('\\', 1)[1]
        if parent == '登录':
            index = self.login_order_list.index(name)
            self.login_info_list[index].update({'name': name, 'info': result})
        else:
            index = self.instruct_order_list.index(name)
            self.instruct_info_list[index].update({'name': name, 'info': result})
            # print(self.instruct_info_list[index])

    def show_instruct(self):
        # print(self.instruct_order_list)
        # print(self.instruct_info_list)
        item = self.instruct_list.currentItem()
        # print(item.parent().text(0))
        ret = self.getLocation(item)  # 获取选中节点父节点
        if ret:
            bin_path = os.path.join(ret, item.text(0))
        else:
            bin_path = os.path.join(item.text(0))
        parent = bin_path.split('\\', 1)[0]
        if parent == '登录':
            item = self.instruct_list.currentItem()
            index = self.login_order_list.index(item.text(0))
            if 'info' in self.login_info_list[index].keys():
                if 'xpath' in self.login_info_list[index]['info'].keys():
                    xpath = "["
                    if self.login_info_list[index]['info']['type'] != 1:
                        xpath += "'" + self.login_info_list[index]['info']['xpath'] + "'" + ","
                    if 'value_table' in self.login_info_list[index]['info'].keys():
                        value_table = self.login_info_list[index]['info']['value_table']
                        for i in range(len(value_table)):
                            xpath += "'" + value_table[i][1] + "'" + ","
                    xpath += "]"
                    self.my_browser.tabs.currentWidget().page().runJavaScript("highlight.highlight(" + xpath + ");")
        else:
            item = self.instruct_list.currentItem()
            index = self.instruct_order_list.index(item.text(0))
            if 'info' in self.instruct_info_list[index].keys():
                if 'xpath' in self.instruct_info_list[index]['info'].keys():
                    xpath = "["
                    if self.instruct_info_list[index]['info']['type'] != 1:
                        xpath += "'" + self.instruct_info_list[index]['info']['xpath'] + "'" + ","
                    if 'value_table' in self.instruct_info_list[index]['info'].keys():
                        value_table = self.instruct_info_list[index]['info']['value_table']
                        for i in range(len(value_table)):
                            xpath += "'" + value_table[i][1] + "'" + ","
                    xpath += "]"
                    self.my_browser.tabs.currentWidget().page().runJavaScript("highlight.highlight(" + xpath + ");")

    def save_file(self):
        filepath, type = QFileDialog.getSaveFileName(self, "保存当前自动化流程", ".\\", 'txt(*.txt)')
        if len(filepath) > 0:
            result = {'login_order': self.login_order_list, 'operation_order': self.instruct_order_list,
                      'login_info': self.login_info_list, 'operation_info': self.instruct_info_list}
            with open('./RunModule/public.pem', "rb") as x:
                f = x.read()
                key = rsa.PublicKey.load_pkcs1(f)
            bts_str = str(result).encode()
            crypto_bytes = rsa_encrypt_bytes(bts_str, key)
            text = base64.b64encode(crypto_bytes).decode()
            with open(filepath, "w") as x:
                x.write(text)
            # with open(filepath + '.json', 'w') as file:
            #     json.dump(result, file, ensure_ascii=False)

    def load_file(self):
        flag = False
        for info in self.login_info_list:
            if len(info['info']['xpath']) > 0:
                flag = True
                break
        if len(self.instruct_order_list) > 0:
            flag = True
        if flag:  # 当前界面有指令
            event = QMessageBox.information(self, '是否保存', '当前界面存在指令，是否保存？',
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                            QMessageBox.Yes)
            if event == QMessageBox.Yes:
                self.save_file()
            elif event == QMessageBox.Cancel:
                return
        filepath, type = QFileDialog.getOpenFileName(self, "加载自动化流程", ".\\", 'txt(*.txt)')
        if len(filepath) > 0:
            with open("./RunModule/private.pem", "rb") as x:
                e = x.read()
                e = rsa.PrivateKey.load_pkcs1(e)
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
                text = base64.b64decode(text)
                d_crypto_bytes = rsa_decrypt(text, e)
                result = eval(d_crypto_bytes)
                # result = json.load(file)
                self.login_order_list = result['login_order']
                self.instruct_order_list = result['operation_order']
                self.login_info_list = result['login_info']
                self.instruct_info_list = result['operation_info']
        self.clear_input()
        self.reload_instruct_list()

    def reload_instruct_list(self):
        operation = self.instruct_list.findItems('操作', QtCore.Qt.MatchContains, column=0)[0]
        num = operation.childCount()
        if num > 0:
            for i in range(num):
                # child被移除后index会减少，所以每次都移除第一个
                operation.removeChild(operation.child(0))
        for j in range(len(self.instruct_order_list)):
            child = QTreeWidgetItem(operation)
            name = self.instruct_order_list[j]
            child.setText(0, name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("OCR&RPA")
    window = MainWindow()
    window.resize(1200, 900)
    window.show()
    app.exec_()
