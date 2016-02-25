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
        6: '参数错误',
        7: '请求方法名错误',
        8: '接口调用失败',
    }
    return {
	    'status': 'fail',
	    'error': error_dict[error_code],
	    'msg': error_param,
	}
def convert_to_str(input_origin):
    if isinstance(input_origin, bytes):
        return input_origin.decode('utf-8')
    elif isinstance(input_origin, str):
        input_origin = input_origin.replace(' ', '').replace('\'','').replace('"','')
        return input_origin
    elif isinstance(input_origin, (int, float)):
        return str(input_origin)
    elif input_origin == None:
        return input_origin
    else:
        try:
            return str(input_origin)
        except:
            return False

def convert_to_int(input_origin):
    if isinstance(input_origin, (int, float)):
        return int(input_origin)
    elif isinstance(input_origin, str):
        input_origin = input_origin.replace(' ', '').replace('\'','').replace('"','')
        try:
            input_origin = int(input_origin)
            return input_origin
        except:
            return False
    elif isinstance(input_origin, bytes):
        return convert_to_int(input_origin.decode('utf-8'))
    else:
        return False

def convert_to_float(input_origin):
    if isinstance(input_origin, (int, float)):
        return float(input_origin)
    elif isinstance(input_origin, str):
        input_origin = input_origin.replace(' ', '').replace('\'','').replace('"','')
        try:
            input_origin = float(input_origin)
            return input_origin
        except:
            return False
    elif isinstance(input_origin, bytes):
        return convert_to_float(input_origin.decode('utf-8'))
    else:
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