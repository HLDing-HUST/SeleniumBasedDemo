import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import QTextCursor, QKeySequence
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from .browser import Ui_MainWindow


class WebEngineView(QWebEngineView):
    def __init__(self, tabWidget):
        super().__init__()
        self.tabWidget = tabWidget

    def createWindow(self, WebWindowType):
        new_webview = WebEngineView(self.tabWidget)
        index = self.tabWidget.addTab(new_webview, '')
        self.tabWidget.setCurrentIndex(index)
        return new_webview


class MyBrowser(QMainWindow):
    def __init__(self):
        super(MyBrowser, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tabs = self.ui.web_tab
        self.tabs.setDocumentMode(True)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.browser = WebEngineView(self.tabs)
        self.browser.setUrl(QUrl("https://www.baidu.com"))  # https://rpa.t.fi-if.top/#/
        self.tabs.addTab(self.browser, self.browser.page().title())
        self.shortcut = QShortcut(QKeySequence("Space"), self)
        self.shortcut.activated.connect(lambda: self.ui.get_xpath.setChecked(not self.ui.get_xpath.isChecked()))

        self.ui.website_input.returnPressed.connect(
            lambda: self.set_url_in_browser(url=self.ui.website_input.text()))
        self.ui.visit.clicked.connect(lambda: self.set_url_in_browser(url=self.ui.website_input.text()))
        self.ui.forward.clicked.connect(self.browser_forward)
        self.ui.backward.clicked.connect(self.browser_back)
        self.ui.refresh.clicked.connect(self.browser_reload)
        self.ui.home.clicked.connect(lambda: self.return_to_home_in_browser())
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.connect_slot(self.browser)

    def connect_slot(self, browser):
        self.ui.get_xpath.stateChanged.connect(lambda: self.set_get_xpath(browser, get_xpath=self.ui.get_xpath.isChecked()))
        browser.urlChanged.connect(self.next_url)
        browser.loadFinished.connect(lambda: self.tabs.setTabText(self.tabs.currentIndex(),
                                                                  browser.page().title()[0:6] + "..." if len(
                                                                      browser.page().title()) > 6 else browser.page().title()))
        browser.loadStarted.connect(self.loadXpathFinder)

    def loadXpathFinder(self):
        script = QWebEngineScript()
        file = QFile("./WebModule/inspect.js")
        if file.open(QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            script.setSourceCode(content.data().decode())
            script.setName("XpathFinder.js")
            # script.setWorldId(QWebEngineScript.MainWorld)
            # script.setInjectionPoint(QWebEngineScript.DocumentReady)  # 在DOM READY的时候注入。也可以在开始的时候注入。
            script.setWorldId(QWebEngineScript.MainWorld)
            script.setInjectionPoint(QWebEngineScript.DocumentReady)
            self.tabs.currentWidget().page().profile().scripts().insert(script)

    def set_get_xpath(self, browser, get_xpath=False):
        if get_xpath:
            # 调用JS中的fullName函数
            browser.page().runJavaScript('xPathFinder.getOptions();')
        else:
            browser.page().runJavaScript('xPathFinder.deactivate();')

    def next_url(self, new_url):
        self.set_url_in_browser(new_url.toString())

    def set_url_in_browser(self, url):
        self.refresh_url_in_website_input(url)
        self.tabs.currentWidget().load(QUrl(url))

    def refresh_url_in_website_input(self, new_url):
        self.ui.website_input.setText(new_url)
        self.ui.website_input.home(False)

    def return_to_home_in_browser(self):
        new_url = "https://www.baidu.com"
        self.refresh_url_in_website_input(new_url)
        self.set_url_in_browser(new_url)
        self.ui.get_xpath.setChecked(False)

    def current_tab_changed(self, i):
        self.connect_slot(self.tabs.currentWidget())
        qurl = self.tabs.currentWidget().url()
        self.refresh_url_in_website_input(qurl.toString())
        # self.update_title(self.tabs.currentWidget())
        self.ui.get_xpath.setChecked(False)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s" % title)

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def add_new_tab(self, qurl=None, label="主页"):
        if qurl is None:
            qurl = QUrl('https://www.baidu.com')
        browser = WebEngineView(self.tabs)
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        self.ui.get_xpath.setChecked(False)

    def browser_forward(self):
        self.tabs.currentWidget().forward()
        self.ui.get_xpath.setChecked(False)

    def browser_back(self):
        self.tabs.currentWidget().back()
        self.ui.get_xpath.setChecked(False)

    def browser_reload(self):
        self.tabs.currentWidget().reload()
        self.ui.get_xpath.setChecked(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("RPA")
    window = MyBrowser()
    window.show()
    app.exec_()
