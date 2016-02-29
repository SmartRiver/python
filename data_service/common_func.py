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

def convert_to_float(input_origin):
    if isinstance(input_origin, (int, float)):
        return float(input_origin)
    elif isinstance(input_origin, str):
        input_origin = input_origin.replace(' ', '').replace('\'','').replace('"','')
        try:
            input_origin = float(input_origin)
            return input_origin
        except:
            raise TypeError('参数格式错误')
    elif isinstance(input_origin, bytes):
        return convert_to_float(input_origin.decode('utf-8'))
    else:
        raise TypeError('参数格式错误')

def _timestamp_check(timestamp_client):
    now_time = int(time.time())
    if -300 < now_time-timestamp_client < 300: # 客户端请求与服务端获取的时间差不超过5分钟，
        return True
    else:
        return False

def pre_token_check(client_token):
    if not isinstance(client_token, str):
        raise Exception('参数应为字符串格式')
    if len(client_token) < 26:
        raise Exception('参数字符位数不小于26位')

def md5_token(client_token):
    key_a = 1237 # 质数因子
    key = '100117108105115104117111' # key = ''.join(str(ord(x)) for x in 'dulishuo') 额外的关键字

    try:
        pre_token_check(client_token)
        msg_client = client_token[:16]
        timestamp_client = client_token[16:26]

        timestamp_client = int(timestamp_client)
        if not _timestamp_check(timestamp_client):
            return False
        # 采用UTC标准时间，取年月日小时
        client_time = time.gmtime(timestamp_client)
        year = client_time.tm_year
        month = client_time.tm_mon
        day = client_time.tm_mday
        hour = client_time.tm_hour

        token_str = ''.join(str(int(x) * key_a) for x in [year, month, day, hour])
        token_str = token_str+key
        #md5加密
        m = hashlib.md5()
        m.update(token_str.encode('utf-8'))
        token_m = m.hexdigest()[:16]

        if msg_client == token_m:
            return True
        else:
            return False
    except Exception as e:
        #raise Exception(exit_error_func(6, str(e)))
        return False