#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this file is used to manage global variables'''

import logging
import logging.config

def _logging_conf():
    '''日志配置'''
    try:
        logging.config.fileConfig('./conf/logging.conf')
        service_logger = logging.getLogger('general')
        error_logger = logging.getLogger('err')
        service_logger.info('--------logging configurating success--------')
        return service_logger, error_logger
    except Exception as e:
        print('--------logging configurating failed--------')

def _load_interface_methods():
    ''' 从配置文件[urf8文件]加载所有开放的接口调用方法和对应的参数*args '''
    _temp_interface_methods = {}
    with open('resource/service/interface_methods.conf', 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line[0] != '#': #跳过注释行
                _temp_value = []
                for x in line.strip().split(':')[1].split('),('):
                    _temp_value.append(tuple(y.strip() for y in x.strip('[]()').split(',')))
                _temp_interface_methods[line.split(':')[0]] = _temp_value
    return _temp_interface_methods

service_logger, error_logger = _logging_conf()
INTERFACE_METHOD = _load_interface_methods() # 接口调用的方法 eg:{方法名：方法参数}