#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this file is used to manage global variables'''

MYSQL_HOST      = None
MYSQL_PORT      = None
MYSQL_USER      = None
MYSQL_PASSWORD  = None

service_logger = None
error_logger = None
INTERFACE_METHOD = {} # 接口调用的方法 eg:{方法名：方法参数}

SELECT_SCHOOL_TARGET_SCORE = {} # 目标档次学校的gpa、toefl\ielts、gre\gmat的分数要求'

SELECT_SCHOOL_OFFER_SCORE = {} # 根据major_id返回关联申请成功的案例offer的平均成绩

# /------------------------institute_info库相关-----------------------------/

INSTITUTE_ID_TO_NAME_EN = {} # 根据id查询学校英文名
INSTITUTE_ID_TO_NAME_ZH = {} # 根据id查询学校中文名

# /------------------------major_info库相关---------------------------------/

MAJOR = {} # 根据id查询专业

# /-------------------------------------------------------------------------/

GPA_SCORE_LEVEL = { # gpa分数对应的系数
    '1.3'   : '3.9-4.1',
    '1'     : '3.75-3.9',
    '0.9'   : '3.6-3.75',
    '0.85'  : '3.5-3.6',
    '0.75'  : '3.35-3.5',
    '0.65'  : '3.2-3.35',
    '0.6'   : '3.0-3.2',
    '0.55'  : '2.9-3.0',
    '0.5'   : '2.8-2.9',
    '0.4'   : '2.6-2.8',
    '0.26'  : '2.4-2.6',
    '0.1'   : '2.0-2.4',
    '0'     : '0.0-2.0'
}
GPA_SCHOOL_LEVEL = { # 本科学校对应的系数
    1   : 1.3,    # 海本综排Top20
    2   : 1.25,   # 海本综排Top21-Top35
    3   : 1.15,   # 海本综排Top36-Top50
    4   : 1.1,    # 海本综排Top51-Top80
    5   : 1,      # 海本综排Top81-Top120
    6   : 1.2,    # 清华北大
    7   : 1.15,   # 综合前十
    8   : 1.1,    # 专业优势学校
    9   : 1,      # 985&211
    10  : 0.9,    # 211
    11  : 0.8,    # 双非一本
    12  : 0.7,    # 双非二本
}