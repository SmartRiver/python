#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this file is used to initialize global variables'''

import logging
import logging.config
import global_variable


def _logging_conf():
    '''日志配置'''
    try:
        logging.config.fileConfig('./conf/logging.conf')
        global_variable.service_logger = logging.getLogger('general')
        global_variable.error_logger = logging.getLogger('err')
        print('--------logging configurating success--------')
    except Exception as e:
        print('--------logging configurating failed--------')

def _load_interface_methods():
    '''从配置文件[utf8文件]加载所有开放的接口调用方法和对应的参数*args'''
    _temp_interface_methods = {}
    with open('./conf/interface_methods.conf', 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line[0] != '#' and len(line) > 1: # 跳过注释行、空白行
                _temp_value = []
                try:
                    for x in line.strip().split(':')[1].split('),('):
                        _temp_value.append(tuple(y.strip() for y in x.strip('[]()').split(',')))
                    _temp_interface_methods[line.split(':')[0]] = _temp_value
                except:
                    print(line)
    global_variable.INTERFACE_METHOD = _temp_interface_methods

def init():
    _logging_conf()
    _load_interface_methods()

init()