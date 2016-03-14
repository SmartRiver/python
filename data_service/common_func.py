# -*- coding: utf:-8 -*-

__author__ = 'johnson'
__doc__ = '''this py file is the collection of those functions or methods used in many other modules'''

import time
import hashlib
import json
from global_variable import service_logger

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
    '''校对客户端请求的时间戳是否在允许范围之内'''
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
    # key = ''.join(str(ord(x)) for x in 'dulishuo') 额外的关键字 ， 取每个字母的ascll码拼接起来
    key = '100117108105115104117111'

    try:
        # 客户端client_token格式、位数校对
        pre_token_check(client_token)
        msg_client = client_token[:16] # 客户端加密后的字符串16位
        timestamp_client = client_token[16:26] # 客户端调用的时间戳，精确到秒
        #时间戳校对，客户端调用和服务端响应时间差 +-5分钟之内通过校对
        timestamp_client = int(timestamp_client)
        if not _timestamp_check(timestamp_client):
            return False
        # 采用UTC标准时间，取年月日小时
        client_time = time.gmtime(timestamp_client)
        year = client_time.tm_year
        month = client_time.tm_mon
        day = client_time.tm_mday
        hour = client_time.tm_hour

        token_str = ''.join(str(int(x) * key_a) for x in [year, month, day, hour]) #将每个元素乘以质数1237再相加
        token_str = token_str+key
        #md5加密
        m = hashlib.md5()
        m.update(token_str.encode('utf-8'))
        token_server = m.hexdigest()[:16]

        if msg_client == token_server:
            return True
        else:
            return False
    except Exception as e:
        #raise Exception(exit_error_func(6, str(e)))
        return False

def process_param_string(input_param, option_param=0):
    try:
        input_param = convert_to_str(input_param)
        input_param = input_param.strip()
        return input_param
    except Exception as e:
        service_logger.error(e)
        if option_param == 1:
            return None
        raise Exception(exit_error_func(1, input_param))

def fetch_params():
    ''' 从self.request.query_arguements里提取出所有的参数（token除外）'''
    

def return_json_dump(input_param):
    '''将返回的json格式数据里的中文Unicode转化为中文'''
    return json.dumps(input_param, ensure_ascii=False, indent=4)

