#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__date__    = '2015-05-25'
__doc__     = 'this script is used to initialize global variables defined in global_variable.py'

import logging
import logging.config
import configparser
import json
import copy
from db_util import MySqlDB
import global_variable as gblvar

def _logging_conf():
    '''日志配置'''
    try:
        logging.config.fileConfig('./conf/logging.conf')
        service_logger = logging.getLogger('general')
        error_logger = logging.getLogger('err')
        service_logger.info('--------logging configurating success--------')
        gblvar.service_logger, gblvar.error_logger = service_logger, error_logger
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
    gblvar.INTERFACE_METHOD =  _temp_interface_methods

def get_default_target_school_score():
    '''获取目标档次学校的gpa、toefl\ielts、gre\gmat的分数要求'''
    # 读取mysql数据库连接参数配置文件
    global MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD

    # 获取该专业的所有的offer成绩
    my_sql = MySqlDB(gblvar.MYSQL_HOST, gblvar.MYSQL_PORT, gblvar.MYSQL_USER, gblvar.MYSQL_PASSWORD, 'hechuang')
    my_cursor = my_sql.get_cursor()
    sql = 'select * from requirement_score'
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    for each in result:
        _temp_major = each['major_id']
        _temp_level = each['school_level']
        if _temp_major in gblvar.SELECT_SCHOOL_TARGET_SCORE:
            gblvar.SELECT_SCHOOL_TARGET_SCORE[_temp_major].update({_temp_level: each})
        else:
            gblvar.SELECT_SCHOOL_TARGET_SCORE.update({_temp_major: {_temp_level: each}})
    
def get_avg_score_by_offer():
    '''根据major_id返回关联申请成功的案例offer的平均成绩'''

    # 获取该专业的所有的offer成绩
    global MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
    
    my_sql = MySqlDB(gblvar.MYSQL_HOST, gblvar.MYSQL_PORT, gblvar.MYSQL_USER, gblvar.MYSQL_PASSWORD, 'hechuang')
    my_cursor = my_sql.get_cursor()

    # 将数据库表中所有的offer的硬性三围分数加载进来
    _cache_offer = {}
    sql = 'select * from offer_hard_condition'
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    _cache_hard_condition = {each['offer_id']: each for each in result}

    sql = 'select offer_id, major_id, institute_id from offer_result where result = %s'
    my_cursor.execute(sql, (1))
    result = my_cursor.fetchall()
    
    _temp_school_avg_score = {}
    _temp_school_avg_count = {}
    for each in result:
        _temp_avg_score = { _ : 0 for _ in ['gpa', 'ielts_total', 'ielts_speaking', 'toefl_total', 'toefl_speaking', 'gre_total', 'gre_writing', 'gmat_total', 'gmat_writing']}
        _temp_avg_count = { _ : 0 for _ in ['gpa', 'ielts_total', 'ielts_speaking', 'toefl_total', 'toefl_speaking', 'gre_total', 'gre_writing', 'gmat_total', 'gmat_writing']}
        _temp_major_id = each['major_id']
        _temp_institute_id = each['institute_id']
        _temp_offer_id = each['offer_id']
        ii = 1
        if _temp_major_id < 1 or _temp_institute_id < 1 or _temp_offer_id < 1: # 过滤无效记录
            continue

        if _temp_major_id in _temp_school_avg_score:
            if _temp_institute_id not in _temp_school_avg_score[_temp_major_id]:
                _temp_school_avg_score[_temp_major_id].update({_temp_institute_id:copy.deepcopy(_temp_avg_score)})
                _temp_school_avg_count[_temp_major_id].update({_temp_institute_id:copy.deepcopy(_temp_avg_count)})
        else:
            _temp_school_avg_score.update({_temp_major_id:{_temp_institute_id:copy.deepcopy(_temp_avg_score)}})
            _temp_school_avg_count.update({_temp_major_id:{_temp_institute_id:copy.deepcopy(_temp_avg_count)}})

        sql = 'select max(gpa) from offer_edu_exp_major where edu_exp_id in (select id from offer_edu_exp where offer_id = %s)'
        my_cursor.execute(sql, (_temp_offer_id))
        _ress = my_cursor.fetchall()
        for each in _ress:
            if isinstance(each['max(gpa)'], str):
                gpa = float(each['max(gpa)'])
                if gpa > 0:
                    _temp_count = _temp_school_avg_count[_temp_major_id][_temp_institute_id]['gpa']
                    _temp_score = _temp_school_avg_score[_temp_major_id][_temp_institute_id]['gpa']
                    _temp_school_avg_score[_temp_major_id][_temp_institute_id]['gpa'] = (_temp_score * _temp_count + gpa) / (_temp_count + 1)
                    _temp_school_avg_count[_temp_major_id][_temp_institute_id]['gpa'] = _temp_count + 1
        _temp_hard_condition = _cache_hard_condition[_temp_offer_id]
        for each in _temp_avg_score:
            if each in _temp_hard_condition:
                if _temp_hard_condition[each] < 0.1: # 过滤无效0分成绩
                    continue
                _temp_count = _temp_school_avg_count[_temp_major_id][_temp_institute_id][each]
                _temp_score = _temp_school_avg_score[_temp_major_id][_temp_institute_id][each]
                _temp_school_avg_score[_temp_major_id][_temp_institute_id][each] = (_temp_score * _temp_count + _temp_hard_condition[each]) / (_temp_count + 1)
                _temp_school_avg_count[_temp_major_id][_temp_institute_id][each] = _temp_count + 1
                
    gblvar.SELECT_SCHOOL_OFFER_SCORE =_temp_school_avg_score

def _load_base_info():
    global MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
    
    my_sql = MySqlDB(gblvar.MYSQL_HOST, gblvar.MYSQL_PORT, gblvar.MYSQL_USER, gblvar.MYSQL_PASSWORD, 'hechuang')
    my_cursor = my_sql.get_cursor()

    sql_institute = 'select * from institute_info'
    my_cursor.execute(sql_institute)
    result = my_cursor.fetchall()
    for each in result:
        gblvar.INSTITUTE_ID_TO_NAME_EN[each['id']] = each['name_en']
        gblvar.INSTITUTE_ID_TO_NAME_ZH[each['id']] = each['name_zh']
        gblvar.INSTITUTE_ID_TO_LOCATION[each['id']] = each['location_type'] if len(each['location_type']) > 0 else 'N/A'

    sql_major = 'select * from major_info'
    my_cursor.execute(sql_major)
    result = my_cursor.fetchall()
    for each in result:
        gblvar.MAJOR[each['id']] = each

    sql_institute_major_level = 'select * from institute_major_level'
    my_cursor.execute(sql_institute_major_level)
    result = my_cursor.fetchall()
    for each in result:
        _temp_major = each['major_id']
        _temp_institute = each['institute_id']
        _temp_level = each['rank_level']    
        _temp_list = []
        if _temp_major in gblvar.INSTITUTE_MAJOR_LEVEL:
            if _temp_level in gblvar.INSTITUTE_MAJOR_LEVEL[_temp_major]:
                _temp_list = gblvar.INSTITUTE_MAJOR_LEVEL[_temp_major][_temp_level]
            _temp_list.append(_temp_institute)
            gblvar.INSTITUTE_MAJOR_LEVEL[_temp_major].update({_temp_level: _temp_list})
        else:
            _temp_list.append(_temp_institute)
            gblvar.INSTITUTE_MAJOR_LEVEL.update({_temp_major: {_temp_level: _temp_list}})
        
def init_db_conf():
    '''初始化数据库连接的一些参数'''
    cf = configparser.ConfigParser()
    cf.read('conf/db.conf')
    s = cf.sections()
    
    gblvar.MYSQL_HOST     = cf.get('mysql_hechuang', 'host')
    gblvar.MYSQL_PORT     = cf.getint('mysql_hechuang', 'port')
    gblvar.MYSQL_USER     = cf.get('mysql_hechuang', 'user')
    gblvar.MYSQL_PASSWORD = cf.get('mysql_hechuang', 'password')

def reload():
    _load_base_info() # 加载一些表的信息（institute_info, major_info）

    _load_interface_methods() # 接口调用的方法 eg:{方法名：方法参数}

    get_default_target_school_score() # 目标档次学校的gpa、toefl\ielts、gre\gmat的分数要求'

    get_avg_score_by_offer() # 根据major_id返回关联申请成功的案例offer的平均成绩

init_db_conf()

_logging_conf()

_load_base_info() # 加载一些表的信息（institute_info, major_info）

_load_interface_methods() # 接口调用的方法 eg:{方法名：方法参数}

get_default_target_school_score() # 目标档次学校的gpa、toefl\ielts、gre\gmat的分数要求'

get_avg_score_by_offer() # 根据major_id返回关联申请成功的案例offer的平均成绩