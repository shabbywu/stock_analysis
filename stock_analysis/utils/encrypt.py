# -*- coding: utf-8 -*-
import base64

from Crypto.Cipher import DES3


def pad(text: str) -> str:
    """
    补齐为8的倍数
    """
    ext_byte_count = len(text) % 8
    if ext_byte_count == 0:
        return text

    add_byte_count = 8 - ext_byte_count
    return text + " " * add_byte_count


def force_text(s, encoding="utf-8", errors="strict"):
    if isinstance(s, bytes):
        return str(s, encoding=encoding, errors=errors)
    return str(s)


class CryptoHandler:
    """
    密码加解密类
    """

    def __init__(
        self,
        secret_key="just-a-placeholder-never-be-used-please-provide-a-key-from-env",
    ):
        self.secret_key = secret_key

    def encrypt(self, text: str) -> bytes:
        """
        加密 数据
        text: app_secret 或者 db password 或者svn password
        """
        text = force_text(text)
        # 补齐8的倍数
        data_string = pad(text)
        # 加密 use triple des
        des3 = DES3.new(self.secret_key, mode=DES3.MODE_CBC, iv=self.secret_key[:8])
        encrypt_data = des3.encrypt(data_string.encode())
        # base64编码, 因为加密后存在很多特殊的字符，防止请求的各种编码问题
        return base64.b64encode(encrypt_data)

    def decrypt(self, text: bytes) -> str:
        """
        解密 数据
        """
        # base64 解码
        raw_data = base64.b64decode(text)
        # des3 解密
        des32 = DES3.new(self.secret_key, mode=DES3.MODE_CBC, iv=self.secret_key[:8])
        decrypt_data = des32.decrypt(raw_data)
        # 去除之前补齐的空格
        decrypt_data = decrypt_data.strip()
        return force_text(decrypt_data)
