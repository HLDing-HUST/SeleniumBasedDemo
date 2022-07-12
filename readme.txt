项目基于PyQt5开发：
images：存放图片以及icon
InstructModule：指令编辑界面，其中qss为大部分控件样式
lib：custom_grips：主界面resize
     MyLineEdit：重写lineEdit控件，加入了自定义tooltip提醒、自定义样式清除button
     resource_rc：resource.qrc生成的py文件
     tooltip：自定义tooltip控件
     Window：界面主窗口文件，功能包括resize、maxsize、minisize、close
     Menu：主界面菜单栏，根据配置实现子界面切换
LoginModule：登录功能
MainWindowModule：主界面功能
WebModule：自定义web功能，包括新页面、主页、前进、后退、刷新、访问、xpath提取
RunModule：自定义RPA执行界面，包括数据的可视化、选择执行、报告输出查看等
RpaReport: 用于存放输出报告
RpaFile: 用于存放生成的RPA文件
SeleniumBase： 重写了部分seleniumbase函数，便于基于数据的选择执行
rpatest.csv: 示例数据文件
rpatest.txt: 示例rpa配置文件
main.py: 主函数所在文件


qss：pyqt的ui样式文件


安装：
pip install -r requirements.txt
pip install --upgrade pip
cd SeleniumBase
pip install -e . --upgrade --no-cache-dir --progress-bar=off