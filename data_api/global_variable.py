#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this file is used to manage global variables'''

service_logger = None # 程序正常运行状态日志
error_logger = None # 异常日志
INTERFACE_METHOD = {} # 接口调用的方法 eg:{方法名：方法参数}

INSTITUTE = {} # 学校库
OFFER = {} # offer录取案例库
PRODUCT = {} # 活动项目库
RANK = {} # 排名库