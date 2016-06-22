#!/usr/bin/python3
# -*-coding:utf-8 -*-

__author__ = 'johnson'
__doc__ = '''this py file is the collection of those functions or methods used in many other modules'''

import time
import hashlib
import json
import configparser
from global_variable import service_logger, GRE_TO_GMAT
from db_util import MySqlDB
import io
import sys
#改变标准输出的默认编码
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

def exit_error_func(error_code, error_param='', return_json_dump=True):
    ''' 格式化错误信息返回 '''
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
    res = {
        'status': 'fail',
        'error': error_dict[error_code],
        'msg': error_param,
    }
    if return_json_dump: # 将返回的json格式数据里的中文Unicode转化为中文
        res = json.dumps(res, ensure_ascii=False, indent=4)
    return res

def convert_var_type(input_origin, dest_type='string'):
    '''将变量转化为指定类型的变量'''
    if isinstance(input_origin, bytes):
        return convert_var_type(input_origin.decode('utf-8'), dest_type)
    if isinstance(input_origin, str): # 去除左右空格，双引号，单引号
        input_origin = input_origin.strip().strip('\'').strip('"')
    try:
        if dest_type == 'int':
            input_origin = int(input_origin)
        elif dest_type == 'float':
            input_origin = float(input_origin)
        elif dest_type == 'string':
            input_origin = str(input_origin)
        elif dest_type == 'dict':
            input_origin = json.loads(input_origin)
        return input_origin
    except:
        raise TypeError('不能将 %s 转换为%s类型数据' % (str(input_origin), dest_type))

def _timestamp_check(timestamp_client):
    '''校对客户端请求的时间戳是否在允许范围之内'''
    now_time = int(time.time())
    if -300 < now_time-timestamp_client < 300: # 客户端请求与服务端获取的时间差不超过5分钟，
        return True
    else:
        return False

def pre_token_check(client_token):
    '''客户端client_token格式、位数校对'''
    if not isinstance(client_token, str):
        raise Exception('参数应为字符串格式')
    if len(client_token) < 26:
        raise Exception('参数字符位数不小于26位')

def md5_token(client_token):
    ''' 这个function是用来校对token '''
    key_a = 1237 # 质数因子
    # key = ''.join(str(ord(x)) for x in 'dulishuo') 额外的关键字 ， 取每个字母的ascll码拼接起来
    key = '100117108105115104117111'

    try:
        pre_token_check(client_token) # 客户端client_token格式、位数校对
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

        return True if msg_client == token_server else False
    except Exception as e:
        raise Exception(exit_error_func(6, str(e)))

def client_token_check(token_requset):
    '''客户端token验证'''
    return md5_token(convert_var_type(token_requset, 'string'))
    
def fetch_params(input_param, *param):
    ''' 从self.request.query_arguements里提取出所有的参数（token除外）'''
    return_param = {}
    for each in param:
        if each[1] == '1': # 必选参数
            if each[0] not in input_param:
                raise Exception('缺乏必要参数:'+each[0])
            return_param[each[0]] = convert_var_type(input_param[each[0]][0], each[2])
        else: # 可选参数
            if each[0] not in input_param:
                return_param[each[0]] = None
            else:
                if len(str(input_param[each[0]][0])) < 4:
                    return_param[each[0]] = None
                else:
                    return_param[each[0]] = convert_var_type(input_param[each[0]][0], each[2])
    return return_param

def return_json_dump(input_param):
    '''将返回的json格式数据里的中文Unicode转化为中文'''
    return json.dumps(input_param, ensure_ascii=False, indent=4)

def convert_ielts_to_toefl(ielts_score):
    '''将ielts分数折算成toefl分数'''
    if not isinstance(ielts_score, (float,int)):
        raise TypeError('输入的ielts分数类型错误')
    if ielts_score > 9.0 or ielts_score < 0:
        raise ValueError('输入的ielts分数不在0-9之间')
    if ielts_score <= 4.0:
        return int(ielts_score*8)
    else:
        return {
            4.5: 33,
            5.0: 40,
            5.5: 53,
            6.0: 69,
            6.5: 79,
            7.0: 97,
            7.5: 105,
            8.0: 112,
            8.5: 116,
            9.0: 119,
        }.get(ielts_score, ValueError('输入的ielts分数格式错误'))
    
def convert_gre_to_gmat(gre_verbal, gre_quantitative):
    '''将gre的verbal和quantitative分数折算成gmat分数'''
    if int(gre_verbal) not in GRE_TO_GMAT:
        raise ValueError('输入的gre的verbal分数不是有效的 {}'.format(gre_verbal))
    elif int(gre_quantitative) not in GRE_TO_GMAT[gre_verbal]:
        raise ValueError('输入的gre的quantitative分数不是有效的 {}'.format(gre_quantitative))
    else:
        print('xxx')
        return GRE_TO_GMAT[gre_verbal][gre_quantitative]

if __name__ == '__main__':
    print(convert_gre_to_gmat(160.0,170))