# rsa 加密
import base64
import json
# 导入rsa库
import rsa.common
import rsa


def generateKey(byte=1024):
    f, e = rsa.newkeys(byte)  # 生成公钥、私钥
    e = e.save_pkcs1()  # 保存为 .pem 格式
    with open("private.pem", "wb") as x:  # 保存私钥
        x.write(e)
    f = f.save_pkcs1()  # 保存为 .pem 格式
    with open("public.pem", "wb") as x:  # 保存公钥
        x.write(f)


def rsa_encrypt_bytes(bytes_str, pubkey):
    if not isinstance(bytes_str, bytes):
        return None

    key_length = rsa.common.byte_size(pubkey.n)
    max_msg_length = key_length - 11

    count = len(bytes_str) // max_msg_length
    if len(bytes_str) % max_msg_length > 0:
        count = count + 1

    cry_bytes = b''

    # rsa加密要以max_msg_length分组, 每组分别加密(加密的数据长度为key_length, 解密时每key_length长度解密然后相加)
    for i in range(count):
        start = max_msg_length * i
        size = max_msg_length
        content = bytes_str[start: start + size]

        # rsa 分组 加密
        crypto = rsa.encrypt(content, pubkey)

        cry_bytes = cry_bytes + crypto

    return cry_bytes


# rsa 解密, bytes_string是rsa_encrypt_hex, rsa_encrypt_bytes的返回值
def rsa_decrypt(bytes_string, pri_key):
    key_length = rsa.common.byte_size(pri_key.n)
    if len(bytes_string) % key_length != 0:
        # 如果数据长度不是key_length的整数倍, 则数据是无效的
        return None

    count = len(bytes_string) // key_length
    d_cty_bytes = b''

    # 分组解密
    for i in range(count):
        start = key_length * i
        size = key_length
        content = bytes_string[start: start + size]

        # rsa 分组 解密
        d_crypto = rsa.decrypt(content, pri_key)

        d_cty_bytes = d_cty_bytes + d_crypto

    return d_cty_bytes


def encode_json(key_path="public.pem", json_path="config.json", text_path="config.txt"):
    with open(key_path, "rb") as x:
        f = x.read()
        key = rsa.PublicKey.load_pkcs1(f)  # load 公钥
    file = open(json_path, 'r', encoding='utf-8')
    m = json.load(file)
    bts_str = str(m).encode()
    crypto_bytes = rsa_encrypt_bytes(bts_str, key)
    text = base64.b64encode(crypto_bytes).decode()
    with open(text_path, "w") as x:  # 保存私钥
        x.write(text)
    return


if __name__ == '__main__':
    # generateKey(1024)
    encode_json(json_path="../a.json", text_path="a.txt")
