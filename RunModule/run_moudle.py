import json
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from .setting import Ui_MainWindow as run_ui
import os
import time

import pytest
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from .setting import Ui_MainWindow
import ctypes
from .gen_python import *
from seleniumbase.console_scripts.sb_install import main
from PyQt5.QtCore import *
from .form import TableDemo


os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = run_ui()
        self.ui.setupUi(self)
        self.p = Thread(self)
        self.web_reload_thread = WebThread(self)
        self.install_driver_thread = installThread(self)
        self.install_flag = True
        self.connect()
        self.state = 'None'
        self.load_setting()
        self.ui.web.setVisible(False)
        self.ui.backward.setVisible(False)
        self.ui.refresh.setVisible(False)
        self.ui.forward.setVisible(False)
        path = './dashboard.html'
        self.modificationTime = os.path.getmtime(path) if os.path.exists(path) else 0

    def connect(self):
        """
        各个控件的槽函数连接
        """
        self.ui.select_data.clicked.connect(lambda: self.select_file(self.ui.data_path, file_type="csv"))
        self.ui.select_config.clicked.connect(lambda: self.select_file(self.ui.config_path, file_type="txt"))
        self.ui.run.clicked.connect(self.open_form)
        self.ui.stop.clicked.connect(self.stop_python)
        self.p.started.connect(self.running)
        self.p.finished.connect(self.finish)
        # self.ui.console.clicked.connect(self.console_control)
        self.ui.save.clicked.connect(self.save_json)
        self.ui.install.clicked.connect(self.install_driver)
        self.install_driver_thread.finished.connect(self.install_finish)
        self.web_reload_thread.trigger.connect(self.set_html)
        self.ui.refresh.clicked.connect(self.browser_reload)
        self.ui.forward.clicked.connect(self.browser_forward)
        self.ui.backward.clicked.connect(self.browser_back)

    # def console_control(self):
    #     """
    #     控制显示台的显示、隐藏
    #     """
    #     if self.console.isChecked():
    #         showConsole()
    #     else:
    #         hideConsole()
    def browser_forward(self):
        self.ui.web.forward()

    def browser_back(self):
        self.ui.web.back()

    def browser_reload(self):
        self.ui.web.reload()

    def select_file(self, textWidget, file_type):
        """
        :param textWidget:显示路径的控件
        :param file_type: 选择文件的类型
        实现选择文件功能
        """
        directory = QtWidgets.QFileDialog.getOpenFileName(None, "选取⽂件", "./",
                                                          "{} Files (*.{})".format(file_type, file_type))
        if directory[0] != '':
            textWidget.setText(directory[0])

    def save_json(self):
        """
        保存配置文件
        """
        with open("setting.json", "w") as f:
            a = {}
            a.update(
                {"demo": self.ui.demo.isChecked(), "console": self.ui.console.isChecked(),
                 "report": self.ui.report.isChecked(),
                 "head": self.ui.head.isChecked(), "max": self.ui.max.isChecked(),
                 "screenshot": self.ui.screenshot.isChecked(),
                 "rs": self.ui.rs.isChecked(), "first_stop": self.ui.first_stop.isChecked(),
                 "thread_num": self.ui.thread_num.text(),
                 "demo_sleep": self.ui.demo_sleep.text(), "highlights": self.ui.highlights.text(),
                 "browser": self.ui.browser.currentIndex(),
                 "config_path": self.ui.config_path.text(), "data_path": self.ui.data_path.text()})
            f.write(json.dumps(a))

    def load_setting(self):
        """
        加载配置文件
        """
        try:
            with open("setting.json", "r") as f:
                m = json.load(f)
                self.ui.demo.setChecked(m["demo"])
                self.ui.console.setChecked(m["console"])
                self.ui.report.setChecked(m["report"])
                self.ui.head.setChecked(m["head"])
                self.ui.max.setChecked(m["max"])
                self.ui.screenshot.setChecked(m["screenshot"])
                self.ui.rs.setChecked(m["rs"])
                self.ui.first_stop.setChecked(m["first_stop"])
                self.ui.thread_num.setValue(int(m["thread_num"]))
                self.ui.demo_sleep.setValue(int(m["demo_sleep"]))
                self.ui.highlights.setValue(int(m["highlights"]))
                self.ui.browser.setCurrentIndex(m["browser"])
                self.ui.config_path.setText(m["config_path"])
                self.ui.data_path.setText(m["data_path"])
        except:
            print('没有配置文件')

    def open_form(self):
        """
        打开可视化数据文件的表单
        """
        # try:
        if self.ui.tab.count() < 2:
            # tab_data = QtWidgets.QWidget()
            # layout = QtWidgets.QVBoxLayout(tab_data)
            self.dataTable = TableDemo(self.ui.data_path.text())
            # layout.addWidget(self.dataTable)
            self.ui.tab.addTab(self.dataTable, "运行数据")
            self.ui.tab.setCurrentIndex(1)

            # self.ui.first = self.dataTable
            # self.dataTable.show()
            self.dataTable.trigger.connect(self.run_python)
        # except:
        #     QMessageBox.about(None, "提示", "解析配置文件失败")
        #     return

    def stop_python(self):
        """
        停止RPA执行程序
        """
        if self.state == 'run':
            # print("注意：暂停后，控制台不显示后续输出")
            self.p.terminate()
            self.p.deleteLater()
            self.state = 'stop'
            self.p = Thread(self)
            self.p.started.connect(self.running)
            self.p.finished.connect(self.finish)
            self.ui.web.reload()
            # self.web_reload_thread.terminate()
            # self.web_reload_thread.deleteLater()
            # self.web_reload_thread = WebThread(self)
            QMessageBox.about(None, "提示", "自动化程序已暂停运行")
        else:
            QMessageBox.about(None, "提示", "没有正在运行的自动化程序")

    def running(self):
        """
        标志RPA程序的正在运行状态
        """
        self.state = 'run'
        self.ui.run.setText("正在运行")

    def install_driver(self):
        """
        安装浏览器驱动
        """
        if self.install_driver_thread.working:
            QMessageBox.about(None, "提示", "当前驱动未安装完成")
        else:
            self.install_flag = True
            if self.ui.browser.currentText() == "火狐":
                self.install_driver_thread.set_driver("geckodriver")
            elif self.ui.browser.currentText() == "ie":
                self.install_driver_thread.set_driver("iedriver")
            elif self.ui.browser.currentText() == "edge":
                self.install_driver_thread.set_driver("edgedriver")
            elif self.ui.browser.currentText() == "谷歌":
                self.install_driver_thread.set_driver("chromedriver")
            self.install_driver_thread.set_version(self.ui.driver.text())
            self.install_driver_thread.start()

    def install_finish(self):
        """
        驱动安装程序执行完毕的调用函数， 提示安装状态
        """
        if not self.install_flag:
            msg = "当前驱动安装失败<br>请使用对应浏览器打开该网址，查看浏览器版本与驱动版本对应关系：<br><a href='https://liushilive.github.io/github_selenium_drivers/index'>https://liushilive.github.io/github_selenium_drivers/index</a><br>"
            QMessageBox.about(None, "关于", msg)
            # QString
            # msg = "BUG Reporting:<a href='https://github.com/xuronghua2001/xxx/issues'>Github</a><br>Update:<a href='https://download.csdn.net/download/duckSoup_2001/xxx'>CSDN</a><br>E-mail:xuronghua2001@outlook.com";
            # QMessageBox::about(nullptr, "关于", msg);
            # QMessageBox.about(None, "提示", "当前驱动安装失败，请使用对应浏览器打开该网址，查看浏览器版本与驱动版本对应关系：https://liushilive.github.io/github_selenium_drivers/index.html")
        else:
            QMessageBox.about(None, "提示", "当前驱动安装完成")

    def set_html(self, html_path):
        """
        :param html_path:需要webengine加载的html
        使web加载对应的html
        """
        self.ui.web.load(QUrl(html_path))

    def finish(self):
        '''
        RPA程序执行完毕的调用函数
        '''
        self.state = 'None'
        self.ui.run.setText("运行")

    def run_python(self):
        '''
        RPA运行程序
        '''
        if self.state == 'run':
            return

        self.ui.tab.removeTab(1)
        config_path = self.ui.config_path.text()
        data_path = self.ui.data_path.text()
        custom_format = '%Y-%m-%d_%H-%M-%S'
        self.current_rpa = "rpa" + datetime.strftime(datetime.now(), custom_format)
        gen_python_path = "./RpaFile/" + self.current_rpa + ".py"
        if config_path == '' or data_path == '':
            QMessageBox.about(None, "提示", "配置文件或数据文件路径不能为空")
        else:
            command = []
            if self.ui.demo.isChecked():
                command.append("--demo")
            if self.ui.head.isChecked():
                command.append("--headless")
            if self.ui.report.isChecked():
                command.append("--html=./RpaReport/" + self.current_rpa + "_report.html")
                command.append("--dashboard")
            if self.ui.max.isChecked():
                command.append("--maximize")
            if self.ui.rs.isChecked():
                command.append("--rs")
            if self.ui.first_stop.isChecked():
                command.append("-x")
            if self.ui.screenshot.isChecked():
                command.append("--screenshot")
            demo_sleep_num = self.ui.demo_sleep.text()
            highlights_num = self.ui.highlights.text()
            thread_num = self.ui.thread_num.text()
            browser_type = self.ui.browser.currentText()
            command.append("--demo_sleep=" + demo_sleep_num)
            command.append("--highlights=" + highlights_num)
            command.append("-n=" + thread_num)
            if browser_type == "火狐":
                command.append("--browser=firefox")
            elif browser_type == "ie":
                command.append("--browser=ie")
            # elif browser_type == "opera":
            #     command.append("--browser=opera")
            # elif browser_type == "Safari":
            #     command.append("--browser=safari")
            elif browser_type == "edge":
                command.append("--browser=edge")
            elif browser_type == "谷歌":
                pass
            if len(self.dataTable.checkedList) > 0:
                for i in self.dataTable.checkedList:
                    command.append(gen_python_path + i)
            else:
                return
            # try:
            generateByInstruct(config_path, data_path, gen_python_path, command)
            # except:
            #     QMessageBox.about(None, "提示", "解析配置文件失败")
            #     return

            # command.append(gen_python_path)
            # self.command = ["--firefox", 'testwebAutomation.py']
            self.command = command
            self.p.start()
            self.state = 'run'
            self.ui.web.setVisible(True)
            self.ui.backward.setVisible(True)
            self.ui.refresh.setVisible(True)
            self.ui.forward.setVisible(True)
            if self.ui.report.isChecked():
                self.web_reload_thread.start()


class Thread(QThread):
    """
    负责执行RPA任务的线程
    """
    trigger = pyqtSignal()

    def __init__(self, window):
        super(Thread, self).__init__()
        self.window = window

    def run(self):
        pytest.main(self.window.command)


class WebThread(QThread):
    """
    负责刷新web的线程
    """
    trigger = pyqtSignal(str)

    def __init__(self, window):
        super(WebThread, self).__init__()
        self.window = window

    def run(self):
        # 若dashboard.html发生了更新，则发送刷新信号
        while self.window.state == 'run':
            self.msleep(1000)
            path = './dashboard.html'
            modificationTime = os.path.getmtime(path) if os.path.exists(path) else 0
            if modificationTime != self.window.modificationTime:
                self.trigger.emit("file:///./dashboard.html")
                self.window.modificationTime = modificationTime
        # 若所有RPA任务执行完毕，则显示最终报告
        if self.window.state == 'None':
            time.sleep(2)
            self.trigger.emit("file:///./RpaReport/" + self.window.current_rpa + "_report.html")


class installThread(QThread):
    """
    负责安装驱动的线程
    """
    trigger = pyqtSignal()

    def __init__(self, window):
        super(installThread, self).__init__()
        self.window = window
        self.working = False
        self.driver = "chromedriver"
        self.version = ""

    def __del__(self):
        self.working = False

    def set_driver(self, driver):
        self.driver = driver

    def set_version(self, version):
        self.version = version

    def run(self):
        self.working = True
        try:
            if self.version == "":
                main(self.driver, "latest")
            else:
                main(self.driver, self.version)
        except:
            self.window.install_flag = False
        self.working = False
