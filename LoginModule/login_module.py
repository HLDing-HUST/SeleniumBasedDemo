import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from lib.Window import Window
from lib.MyLineEdit import MyLineEdit
from lib.tooltip import ToolTip
from .login import Ui_MainWindow as login_ui
import os
import requests

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):
    # 定义登录信号
    login_signal = pyqtSignal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = login_ui()
        self.ui.setupUi(self)
        self.init_login_register_lineedit()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        function_list = [{'function': 'minimize', 'name': 'minimizeAppBtn'},
                         {'function': 'close', 'name': 'closeAppBtn'}]
        self.Window = Window(self, function_list)
        self.init_slot_function()
        self.login_cookies = None
        self.login_headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            "Content-Type":
                "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 添加提示
        self.toolTip = ToolTip(ContentsMargins=(15, 10, 15, 10), font_size=10, direction='middle', parent=self)
        self.toolTip.setTheme('normal', True)
        self.toolTip.hide()

    def init_login_register_lineedit(self):
        chinese_and_letter = "[a-z|A-Z|\u4e00-\u9fa5]+$"
        letter_and_number_and_ = "[a-z|A-Z|0-9|_]+$"
        # 登录
        username = MyLineEdit("username", "用户名", 40, 'Normal',
                              letter_and_number_and_, "仅限英文、数字、下划线", self.ui.info)
        password = MyLineEdit("password", "密码", 40, 'Password',
                              letter_and_number_and_, "仅限英文、数字、下划线", self.ui.info)
        self.ui.login_layout.addWidget(username)
        self.ui.login_layout.addWidget(password)
        # 注册
        register_name = MyLineEdit("register_name", "姓名", 40, 'Normal',
                                   chinese_and_letter, "仅限汉字和英文", self.ui.register_info)
        register_username = MyLineEdit("register_username", "用户名", 40, 'Normal',
                                       letter_and_number_and_, "仅限英文、数字、下划线", self.ui.register_info)
        register_password = MyLineEdit("register_password", "密码", 40, 'Password',
                                       letter_and_number_and_, "仅限英文、数字、下划线", self.ui.register_info)
        register_repassword = MyLineEdit("register_repassword", "确认密码", 40, 'Password',
                                         letter_and_number_and_, "仅限英文、数字、下划线", self.ui.register_info)
        self.ui.register_layout.addWidget(register_name)
        self.ui.register_layout.addWidget(register_username)
        self.ui.register_layout.addWidget(register_password)
        self.ui.register_layout.addWidget(register_repassword)

    def init_slot_function(self):
        self.ui.register_lable.mousePressEvent = self.switch_to_register
        self.ui.login_lable.mousePressEvent = self.switch_to_login
        self.ui.login_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.register)
        self.ui.login_button.setShortcut(QKeySequence('Return'))
        self.ui.register_button.setShortcut(QKeySequence('Return'))

    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

    def switch_to_register(self, event):
        # 隐藏注册提示
        self.ui.register_layout.itemAt(0).widget().hide_tooltip()
        self.ui.register_layout.itemAt(1).widget().hide_tooltip()
        self.ui.register_layout.itemAt(2).widget().hide_tooltip()
        self.ui.register_layout.itemAt(3).widget().hide_tooltip()
        # 隐藏提示
        self.toolTip.hide()
        # 切换到注册界面
        self.ui.stackedWidget.setCurrentWidget(self.ui.registerPage)

    def switch_to_login(self, event):
        # 隐藏登录提示
        self.ui.login_layout.itemAt(0).widget().hide_tooltip()
        self.ui.login_layout.itemAt(1).widget().hide_tooltip()
        # 隐藏提示
        self.toolTip.hide()
        # 切换到登录界面
        self.ui.stackedWidget.setCurrentWidget(self.ui.loginPage)

    def login(self):
        username = self.ui.login_layout.itemAt(0).widget().text()
        password = self.ui.login_layout.itemAt(1).widget().text()
        if len(username) == 0:
            self.ui.login_layout.itemAt(0).widget().show_tooltip('用户名不能为空', 'warning', 2)
        if len(password) == 0:
            self.ui.login_layout.itemAt(1).widget().show_tooltip('密码不能为空', 'warning', 2)
        if len(username) > 0 and len(password) > 0:
            data = {'username': username,
                    'password': password}
            print(data)
            print('登陆成功')
            self.toolTip.show_tips("success", True, '登陆成功', 2)
            self.login_cookies = None
            self.login_signal.emit(username)
            # 与服务器进行通信，认证登录
            '''
            try:
                response = requests.post('http://127.0.0.1:8009/app_login',
                                         headers=self.login_headers,
                                         data=data,
                                         allow_redirects=False)
                result = json.loads(response.text)
                if result['status'] == 0:
                    print('用户名或密码错误')
                    self.toolTip.show_tips("error", True, '用户名或密码错误', 2)
                elif result['status'] == 1:
                    print('登陆成功')
                    self.toolTip.show_tips("success", True, '登陆成功', 2)
                    self.login_cookies = response.cookies
                    self.login_signal.emit(username)
                elif result['status'] == 2:
                    self.toolTip.show_tips("warning", True, '权限不够', 2)
                    print('权限不够')
            except:
                self.toolTip.show_tips("error", True, '与服务器失去连接...', 2)
                print('与服务器失去连接...')
            '''

    def register(self):
        name = self.ui.register_layout.itemAt(0).widget().text()
        username = self.ui.register_layout.itemAt(1).widget().text()
        password = self.ui.register_layout.itemAt(2).widget().text()
        repassword = self.ui.register_layout.itemAt(3).widget().text()
        if len(name) == 0:
            self.ui.register_layout.itemAt(0).widget().show_tooltip('姓名不能为空', 'warning', 2)
        if len(username) == 0:
            self.ui.register_layout.itemAt(1).widget().show_tooltip('用户名不能为空', 'warning', 2)
        if len(password) == 0:
            self.ui.register_layout.itemAt(2).widget().show_tooltip('密码不能为空', 'warning', 2)
        if len(repassword) == 0:
            self.ui.register_layout.itemAt(3).widget().show_tooltip('确认密码不能为空', 'warning', 2)
        if len(name) > 0 and len(username) > 0 and len(password) > 0 and len(repassword) > 0:
            if password != repassword:
                self.ui.register_layout.itemAt(3).widget().show_tooltip('密码不一致', 'error', 2)
            else:
                data = {'name': name,
                        'username': username,
                        'password': password,
                        'repassword': repassword}
                print(data)
                print('注册成功')
                '''
                try:
                    response = requests.post('http://127.0.0.1:8009/app_register',
                                             headers=self.login_headers,
                                             data=data,
                                             allow_redirects=False)
                    result = json.loads(response.text)
                    if result['status'] == 0:
                        self.ui.register_layout.itemAt(3).widget().show_tooltip('密码不一致', 'error', 2)
                    elif result['status'] == 1:
                        print('注册成功')
                        self.toolTip.show_tips("success", True, '注册成功，请联系管理员更改权限', 2)
                    elif result['status'] == 2:
                        self.ui.register_layout.itemAt(1).widget().show_tooltip('用户名已存在', 'error', 2)
                        # print('用户名已存在')
                except:
                    self.toolTip.show_tips("error", True, '与服务器失去连接...', 2)
                    print('与服务器失去连接...')
                '''