# -*- coding: utf-8 -*-
import re


def normalize_stock_code(code):
    """
    上海证券交易所证券代码分配规则
    https://biz.sse.com.cn/cs/zhs/xxfw/flgz/rules/sserules/sseruler20090810a.pdf

    深圳证券交易所证券代码分配规则
    http://www.szse.cn/main/rule/bsywgz/39744233.shtml
    """
    if isinstance(code, int):
        suffix = "XSHG" if code >= 500000 else "XSHE"
        return "%06d.%s" % (code, suffix)
    elif isinstance(code, str):
        code = code.upper()
        if code[-5:] in (".XSHG", ".XSHE", ".CCFX"):
            return code
        match = re.search(r"[0-9]{6}", code)
        if match is None:
            raise ValueError("wrong code={}".format(code))
        number = match.group(0)

        if "SH" in code:
            suffix = "XSHG"
        elif "SZ" in code:
            suffix = "XSHE"
        else:
            suffix = "XSHG" if int(number) >= 500000 else "XSHE"
        return f"{number}.{suffix}"
    else:
        raise ValueError("normalize_code(code=%s) 的参数必须是字符串或者整数".format(code))
