# -*- coding: utf:-8 -*-

__author__ = 'johnson'
__doc__ = '''this py file is the collection of those functions or methods used in many other modules'''

import time
import hashlib

def exit_error_func(error_code, error_param=''):
    error_dict = {
		1: '参数格式错误',
	    2: '参数内容错误',
	    3: '程序内部错误',
	    4: '验证失败',
        5: '缺失必要参数',
    }
    return {
	    'status': 'fail',
	    'error': error_dict[error_code],
	    'msg': error_param,
	}
def convert_to_str(input_str):
    if isinstance(input_str, bytes):
        return input_str.decode('utf-8')
    elif isinstance(input_str, str):
        return input_str
    elif isinstance(input_str, (int, float)):
        return repr(input_str)
    elif input_str == None:
        return input_str
    else:
        try:
            return repr(input_str)
        except:
            return False


def md5_token(token_key='dulishuo0306'):
    now = time.gmtime() # 获取当前UTC统一时间，与时区无关

    year = now.tm_year * 1
    month = now.tm_mon * 12
    day = now.tm_mday * 30
    hour = now.tm_hour * 60

    token_before = token_key+str(year+month+day+hour)

    m = hashlib.md5()
    m.update(token_before.encode('utf-8'))
    token = m.hexdigest()[:16]

    return token