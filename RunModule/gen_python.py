import base64
import json
import rsa
from .encode import rsa_decrypt


def generate(config_path="config.txt", data_path="C:\\\\Users\\\\DHL\\\\Desktop\\\\data.csv",
             gen_python_path="testwebAutomation.py", args=None):
    with open("./RunModule/private.pem", "rb") as x:
        e = x.read()
        e = rsa.PrivateKey.load_pkcs1(e)
    with open(config_path, "r", encoding='utf-8') as x:  # 保存私钥
        text = x.read()
    text = base64.b64decode(text)
    d_crypto_bytes = rsa_decrypt(text, e)

    # f = open(config_path, 'r', encoding='utf-8')
    # m = json.load(f)
    m = eval(d_crypto_bytes)
    pyFile = open(gen_python_path, 'w')
    startCode = "import csv\nimport pytest\nimport unittest\nfrom seleniumbase import BaseCase\n" \
                "from parameterized import parameterized" \
                "\n\ndata = csv.reader(open(\'{}\', \'r\', encoding='utf_8'))\ninput = []\nfor i in data:\n\tinput.append([i])" \
                "\n\n\nclass MyTestClass(BaseCase):\n\t@parameterized.expand(input)\n\t" \
                "def test_swag_labs(self, arg_list):\n".format(data_path)  # \nimport ddddocr
    pyFile.write(startCode)
    command = '\t\tself.open(\'{}\')\n'.format(m["url"]["http"])
    pyFile.write(command)

    if len(m["login"]) > 0:
        if m["login"][-2]["type"] == "verification":
            command = "\t\tocr = ddddocr.DdddOcr()\n"
            pyFile.write(command)
        if m["login"][-1]["type"] == "click":
            command = "\t\twhile self.is_element_enabled(\'{}\'):\n".format(m["login"][-1]["CSS_SELECTOR"])
            pyFile.write(command)
        for cmd in m["login"]:
            command = ""
            if cmd["type"] == "url":
                command = '\t\t\tself.open(\'{}\')\n'.format(cmd["http"])
            elif cmd["type"] == "text":
                command = '\t\t\tself.type(\'{}\', {})\n'.format(cmd["CSS_SELECTOR"], cmd["value"])
            elif cmd["type"] == "click":
                command = '\t\t\tself.click(\'{}\')\n'.format(cmd["CSS_SELECTOR"])
            elif cmd["type"] == "multiple":
                command = '\t\t\tself.multiple_self({}, {})\n'.format(cmd["CSS_SELECTOR_LIST"], cmd["value"])
            elif cmd["type"] == "single":
                command = '\t\t\tself.single_self(\'{}\', {})\n'.format(cmd["CSS_SELECTOR"], cmd["value"])
            elif cmd["type"] == "verification":
                command = '\t\t\tself.save_screenshot("verification", selector=\'{}\')\n' \
                          '\t\t\twith open("verification.png", \'rb\') as f:\n' \
                          '\t\t\t\timage = f.read()\n' \
                          '\t\t\tres = ocr.classification(image)\n' \
                          '\t\t\tself.type(\'{}\', res)\n'.format(cmd["CSS_SELECTOR_LIST"][1]["CSS_SELECTOR"],
                                                                  cmd["CSS_SELECTOR_LIST"][0]["CSS_SELECTOR"])
            if command != "":
                pyFile.write(command)

    for cmd in m["list"]:
        command = ""
        if cmd["type"] == "url":
            command = '\t\tself.open(\'{}\')\n'.format(cmd["http"])
        elif cmd["type"] == "text":
            command = '\t\tself.type(\'{}\', {})\n'.format(cmd["CSS_SELECTOR"], cmd["value"])
        elif cmd["type"] == "click":
            command = '\t\tself.click(\'{}\')\n'.format(cmd["CSS_SELECTOR"])
        elif cmd["type"] == "select":
            if len(cmd["CSS_SELECTOR_LIST"]) > 1:
                command = '\t\tself.multiple_self({}, {})\n'.format(cmd["CSS_SELECTOR_LIST"], cmd["value"])
            else:
                command = '\t\tself.single_self(\'{}\', {})\n'.format(cmd["CSS_SELECTOR_LIST"][0]["CSS_SELECTOR"],
                                                                      cmd["value"])
        elif cmd["type"] == "drop-down":
            command = '\t\tself.click(\'{}\')\n'.format(cmd["CSS_SELECTOR"])
            command += '\t\tself.multiple_self({}, {})\n'.format(cmd["CSS_SELECTOR_LIST"], cmd["value"])
            # command = '\t\tself.single_self(\'{}\', {})\n'.format(cmd["CSS_SELECTOR"], cmd["value"])
        if command != "":
            pyFile.write(command)
    command = "\n\nif __name__ == '__main__':\n\tpytest.main({})".format(args)
    pyFile.write(command)
    pyFile.close()


def generateByInstruct(config_path="config.txt", data_path="C:\\\\Users\\\\DHL\\\\Desktop\\\\data.csv",
                       gen_python_path="testwebAutomation.py", args=None):
    with open("./RunModule/private.pem", "rb") as x:
        e = x.read()
        e = rsa.PrivateKey.load_pkcs1(e)
    with open(config_path, "r", encoding='utf-8') as x:  # 保存私钥
        text = x.read()
    text = base64.b64decode(text)
    d_crypto_bytes = rsa_decrypt(text, e)

    m = eval(d_crypto_bytes)
    loginInfo = m["login_info"]
    url, user, pwd, val, val_img, login = loginInfo[0], loginInfo[1], loginInfo[2], loginInfo[3], loginInfo[4], \
                                          loginInfo[5]
    pyFile = open(gen_python_path, 'w')
    startCode = "import csv\nimport pytest\nimport unittest\nfrom seleniumbase import BaseCase\n" \
                "from parameterized import parameterized" \
                "\n\ndata = csv.reader(open(\'{}\', \'r\', encoding='utf_8'))\ninput = []\nfor i in data:\n\tinput.append([i])" \
                "\n\n\nclass MyTestClass(BaseCase):\n" \
                "\t@parameterized.expand(input)\n\tdef test_rpa(self, arg_list):\n".format(data_path)  # \nimport ddddocr
    pyFile.write(startCode)

    # 打开网址
    assert url["info"]["xpath"] != "", "登陆网址不能为空"
    command = '\t\tself.open(\'{}\')\n'.format(url["info"]["xpath"])
    pyFile.write(command)
    if login["info"]["xpath"] != "":
        assert login["name"] == "登录按钮"
        verification = val["info"]["xpath"] != "" and val_img["info"]["xpath"] != ""
        if verification:
            pyFile.write("\t\timport ddddocr\n")
            pyFile.write("\t\tocr = ddddocr.DdddOcr()\n")
            pyFile.write("\t\twhile self.is_element_enabled(\'{}\'):\n".format(login["info"]["xpath"]))

        # 填入用户名
        if user["info"]["xpath"] != "":
            assert user["name"] == "用户名"
            command = '\t\tself.type(\'{}\', \'{}\')\n'.format(user["info"]["xpath"], user["info"]["extra_input"])
            command = '\t' + command if verification else command
            pyFile.write(command)

        # 填入密码
        if pwd["info"]["xpath"] != "":
            assert pwd["name"] == "密码"
            command = '\t\tself.type(\'{}\', \'{}\')\n'.format(pwd["info"]["xpath"], pwd["info"]["extra_input"])
            command = '\t' + command if verification else command
            pyFile.write(command)

        # 验证码
        if verification:
            assert val["name"] == "验证码"
            assert val_img["name"] == "验证码图片"
            command = '\t\t\tself.save_screenshot("./images/verification", selector=\'{}\')\n' \
                      '\t\t\twith open("./images/verification.png", \'rb\') as f:\n' \
                      '\t\t\t\timage = f.read()\n' \
                      '\t\t\tres = ocr.classification(image)\n' \
                      '\t\t\tself.type(\'{}\', res)\n'.format(val_img["info"]["xpath"], val["info"]["xpath"])
            pyFile.write(command)

        # 登陆
        command = '\t\tself.click(\'{}\')\n'.format(login["info"]["xpath"])
        command = '\t' + command if verification else command
        pyFile.write(command)

    # 执行RPA操作
    '''
        type: 0为打开网址， 1为点击， 2为输入文本， 3为单选， 4为多选 ，5为获取元素
    '''
    for operation in m["operation_info"]:
        command = ""
        if operation["info"]["type"] == 0:
            command = '\t\tself.open(\'{}\')\n'.format(operation["info"]["xpath"])
        elif operation["info"]["type"] == 1:
            command = '\t\tself.click(\'{}\')\n'.format(operation["info"]["xpath"])
        elif operation["info"]["type"] == 2:
            index = 'arg_list[{}]'.format(operation["info"]["index"])
            command = '\t\tself.type(\'{}\', {})\n'.format(operation["info"]["xpath"], index)
        elif operation["info"]["type"] == 3:
            index = 'arg_list[{}]'.format(operation["info"]["index"])
            xpath_list = [xpath[1] for xpath in operation["info"]["value_table"]]
            command = '\t\tself.click(\'{}\')\n'.format(operation["info"]["xpath"])
            command += '\t\tself.single_self({}, {})\n'.format(xpath_list, index)
        elif operation["info"]["type"] == 4:
            index = 'arg_list[{}]'.format(operation["info"]["index"])
            xpath_list = [xpath[1] for xpath in operation["info"]["value_table"]]
            command = '\t\tself.click(\'{}\')\n'.format(operation["info"]["xpath"])
            command += '\t\tself.multiple_self({}, {})\n'.format(xpath_list, index)
        if command != "":
            pyFile.write(command)
    pyFile.close()


def isElementExist(driver, element):
    browser = driver
    try:
        browser.find_element_by_css_selector(element)
        return True
    except:
        return False


if __name__ == '__main__':
    # generate()
    # generate(config_path='rpaTest.json')
    generateByInstruct(config_path='../rpatest.txt', data_path='../rpatest.csv')
