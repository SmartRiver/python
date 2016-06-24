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
from pyexcel_xls import get_data
from db_util import MySqlDB
import global_variable as gblvar
from common_func import (convert_gre_to_gmat, convert_ielts_to_toefl)

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
    
def _get_gpa_score(_score, _institute, _full_score):
    if _institute not in gblvar.SCHOOL_LEVEL:
        return None
    else:
        for each in gblvar.GPA_SCORE_LEVEL:
            _temp_value = gblvar.GPA_SCORE_LEVEL[each]
            if float(_temp_value.split('-')[0]) <= _score < float(_temp_value.split('-')[1]):
                _gpa_score = float('{:.2f}'.format(float(each) * _full_score * gblvar.GPA_SCHOOL_LEVEL[gblvar.SCHOOL_LEVEL[_institute]]))
        return _gpa_score
    return None
    
def _get_toefl_ielts_score(_score, _full_score):
    for each in gblvar.IBT_LEVEL:
        if int(each.split('-')[0]) <= _score <= int(each.split('-')[1]):
            return float('{:.2f}'.format(_full_score * gblvar.IBT_LEVEL[each]))
    return None

def _get_gre_gmat_score(_score, _full_score, _major):
    _temp_rule = {}
    if gblvar.MAJOR[_major]['belong_to'] == 4:
        _temp_rule = gblvar.GMAT_LEVEL.copy()
    else:
        _temp_rule = gblvar.GRE_LEVEL.copy()
    for each in _temp_rule:
        if int(each.split('-')[0]) <= _score <= int(each.split('-')[1]):
            return float('{:.2f}'.format(_full_score * _temp_rule[each]))
    return None
        
def _get_total_score(offer, _major):
    '''按照规则将gpa, toefl/ielts, gre/gmat统计成一个分数，这个分数用于排序'''
    _full_score = gblvar.SUBJECT_SCORE.get(gblvar.MAJOR[_major]['name_en'], '35-30-25')
    _gpa_score = _get_gpa_score(offer['_gpa'], offer['background_institute_level'], int(_full_score.split('-')[0]))
    _toefl_ielts_score = _get_toefl_ielts_score(offer['_toefl_ielts'], int(_full_score.split('-')[1]))
    _gre_gmat_score = _get_gre_gmat_score(offer['_gre_gmat'], int(_full_score.split('-')[2]), _major)

    if None in [_gpa_score, _toefl_ielts_score, _gre_gmat_score]:
        return None
    else:
        return sum([_gpa_score, _toefl_ielts_score, _gre_gmat_score])
    

def _calculate_most_percent_offer(offer_list, _major, percent=0.8):
    '''按学校专业取中间80%学生的分数，并统一换算成gpa, toefl/ielts, gre/gmat'''
    _score_list = []
    for each in offer_list:
        _temp_score = _get_total_score(each, _major)
        if _temp_score != None:
            _score_list.append(_temp_score)
    _len = len(_score_list)
    if _len == 0:
        return None
    elif _len < 10: # 案例过少不做处理
        _temp_avg = round(sum(_score_list)/_len, 2)
        print(_score_list)
        _filter_score_list = list(filter(lambda x : abs(x - _temp_avg) < 10, _score_list)) # 去除极大极小值
        print(_filter_score_list)
        print(_temp_avg)
        if len(_filter_score_list) == 0:
            return None
        return round(sum(_filter_score_list)/len(_filter_score_list), 2)
        
    else:
        _score_list.sort()
        _start_index    = int(_len * ((1-percent)/2))
        _end_index      = _len - _start_index
        return round(sum(_score_list[_start_index, _end_index]) ,2)
    
def _get_gre_gmat(_temp_gre, _temp_verbal, _temp_quantitative, _temp_gmat):
    '''将gre转换为gmat'''
    if _temp_gre >= 260:
        if _temp_verbal < 130 and _temp_quantitative >= 130:
            _temp_verbal = _temp_gre - _temp_quantitative
        if _temp_verbal >= 130 and _temp_quantitative < 130:
            _temp_quantitative = _temp_gre - _temp_verbal
    if _temp_verbal >= 130 and _temp_quantitative >= 130:
        _return = convert_gre_to_gmat(_temp_verbal, _temp_quantitative)
        if _return > _temp_gmat:
            return _return
        else:
            return _temp_gmat
    elif _temp_gmat > 200:
        return _temp_gmat
    else:
        return None

def _get_toefl_ielts(_toefl, _ielts):
    '''将ielts转化为toefl'''
    if _ielts > 0 and _toefl <= 0:
        return convert_ielts_to_toefl(_ielts)
    elif _ielts > 0 and _toefl > 0:
        if convert_ielts_to_toefl(_ielts) < _toefl:
            return _toefl
        else:
            return convert_ielts_to_toefl(_ielts)
    else:
        return _toefl

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
    
    # _temp_school_avg_score = {}
    # _temp_school_avg_count = {}
    _temp_major_school_offer = {}
    for each in result:
        # _temp_avg_score = { _ : 0 for _ in ['gpa', 'ielts_total', 'ielts_speaking', 'toefl_total', 'toefl_speaking', 'gre_total', 'gre_writing', 'gmat_total', 'gmat_writing']}
        # _temp_avg_score = { _ : 0 for _ in ['gpa', 'ielts_total', 'ielts_speaking', 'toefl_total', 'toefl_speaking', 'gre_total', 'gre_writing', 'gmat_total', 'gmat_writing']}
        # _temp_avg_count = { _ : 0 for _ in ['gpa', 'ielts_total', 'ielts_speaking', 'toefl_total', 'toefl_speaking', 'gre_total', 'gre_writing', 'gmat_total', 'gmat_writing']}
        
        _temp_major_id = each['major_id']
        _temp_institute_id = each['institute_id']
        _temp_offer_id = each['offer_id']
        
        if _temp_major_id < 1 or _temp_institute_id < 1 or _temp_offer_id < 1: # 过滤无效记录
            continue
        _toefl_gre = _cache_hard_condition[_temp_offer_id]
        if _toefl_gre['toefl_total'] < 1 and _toefl_gre['ielts_total'] < 1: # 过滤同时缺失toefl和ielts成绩的案例
            continue
        elif _toefl_gre['gre_total'] < 260 and _toefl_gre['gmat_total'] < 200: # 过滤同时缺失gre和gmat成绩的案例
            continue
        
        _toefl_ielts = _get_toefl_ielts(_toefl_gre['toefl_total'], _toefl_gre['ielts_total'])
        if gblvar.MAJOR[_temp_major_id]['belong_to'] == 4: # 商科的将gre转换为gmat成绩
            _gre_gmat = _get_gre_gmat(_toefl_gre['gre_total'], _toefl_gre['gre_verbal'], _toefl_gre['gre_quantitative'], _toefl_gre['gmat_total'])
            if _gre_gmat == None:
                continue
        else:
            _gre_gmat = _toefl_gre['gre_total']
            if _gre_gmat < 260:
                continue

        # if _temp_major_id in _temp_school_avg_score:
        #     if _temp_institute_id not in _temp_school_avg_score[_temp_major_id]:
        #         _temp_school_avg_score[_temp_major_id].update({_temp_institute_id:copy.deepcopy(_temp_avg_score)})
        #         _temp_school_avg_count[_temp_major_id].update({_temp_institute_id:copy.deepcopy(_temp_avg_count)})
        # else:
        #     _temp_school_avg_score.update({_temp_major_id:{_temp_institute_id:copy.deepcopy(_temp_avg_score)}})
        #     _temp_school_avg_count.update({_temp_major_id:{_temp_institute_id:copy.deepcopy(_temp_avg_count)}})

        sql = 'select max(gpa) from offer_edu_exp_major where edu_exp_id in (select id from offer_edu_exp where offer_id = %s)'
        my_cursor.execute(sql, (_temp_offer_id))
        _gpa = my_cursor.fetchone()
        _gpa = _gpa['max(gpa)']
        if _gpa == None: # 过滤缺失gpa成绩的案例
            continue
        elif float(_gpa) <= 0.1:
            continue
        # 获取offer对应的背景学校档次
        _temp_sql = 'select background_institute_level from offer_edu_exp where offer_id = %s'
        my_cursor.execute(_temp_sql, (_temp_offer_id))
        _institute_level = my_cursor.fetchone()['background_institute_level']
        if _institute_level not in gblvar.SCHOOL_LEVEL:
            continue

        each.update({'_gpa': float(_gpa), '_toefl_ielts': _toefl_ielts, '_gre_gmat': _gre_gmat, 'background_institute_level': _institute_level})
        if _temp_major_id not in _temp_major_school_offer:
            _temp_major_school_offer.update({_temp_major_id: {_temp_institute_id: [each]}})
        else:
            _temp_offer_list = []
            if _temp_institute_id in _temp_major_school_offer[_temp_major_id]:
                _temp_offer_list = _temp_major_school_offer[_temp_major_id][_temp_institute_id]
            _temp_offer_list.append(each)
            _temp_major_school_offer[_temp_major_id].update({_temp_institute_id: _temp_offer_list})

    for major_key in _temp_major_school_offer: # offer计算
        for school_key in _temp_major_school_offer[major_key]:
            _avg_score =  _calculate_most_percent_offer(_temp_major_school_offer[major_key][school_key], major_key)
            if _avg_score != None:
                _temp_major_school_offer[major_key][school_key] = _avg_score
                print(_avg_score)
        # for each in _ress:
        #     if isinstance(each['max(gpa)'], str):
        #         gpa = float(each['max(gpa)'])
        #         if gpa > 0:
        #             _temp_count = _temp_school_avg_count[_temp_major_id][_temp_institute_id]['gpa']
        #             _temp_score = _temp_school_avg_score[_temp_major_id][_temp_institute_id]['gpa']
        #             _temp_school_avg_score[_temp_major_id][_temp_institute_id]['gpa'] = (_temp_score * _temp_count + gpa) / (_temp_count + 1)
        #             _temp_school_avg_count[_temp_major_id][_temp_institute_id]['gpa'] = _temp_count + 1
        # _temp_hard_condition = _cache_hard_condition[_temp_offer_id]
        # for each in _temp_avg_score:
        #     if each in _temp_hard_condition:
        #         if _temp_hard_condition[each] < 0.1: # 过滤无效0分成绩
        #             continue
        #         _temp_count = _temp_school_avg_count[_temp_major_id][_temp_institute_id][each]
        #         _temp_score = _temp_school_avg_score[_temp_major_id][_temp_institute_id][each]
        #         _temp_school_avg_score[_temp_major_id][_temp_institute_id][each] = (_temp_score * _temp_count + _temp_hard_condition[each]) / (_temp_count + 1)
        #         _temp_school_avg_count[_temp_major_id][_temp_institute_id][each] = _temp_count + 1
    for major_key in _temp_major_school_offer: # offer计算
        for school_key in _temp_major_school_offer[major_key]:
            #print('{}    {}    {}'.format(major_key,school_key,_temp_major_school_offer[major_key][school_key]))          
            pass
    gblvar.SELECT_SCHOOL_OFFER_SCORE =_temp_major_school_offer

def _load_convert_rule():
    '''加载一些常用的分数换算规则'''
    try:
        data_gre = get_data('resource/GRE-GMAT换算.xlsx', streaming=True)
        data_gmat = get_data('resource/GMAT-GRE换算.xlsx', streaming=True)
    except Exception as e:
        gblvar.error_logger.error('what is wrong')
        gblvar.error_logger.error('{}\n{}'.format(str(e), '/resource/GRE-GMAT换算.xlsx加载失败'))
        exit(-1)
    gre_q_key = []
    for each in data_gre:
        if len(each) > 10: # 过滤注释、标题
            if not isinstance(each[1], float):
                gre_q_key = [int(x) for x in each[2:]]
            else:
                for index, item in enumerate(each[2:]):
                    _temp_key = int(each[1])
                    item = int(item)
                    if _temp_key not in gblvar.GRE_TO_GMAT:
                        gblvar.GRE_TO_GMAT.update({_temp_key: {gre_q_key[index]: item}})
                    else:
                        gblvar.GRE_TO_GMAT[_temp_key].update({gre_q_key[index]: item})
    for each in data_gmat:
        if isinstance(each[0], float):
            gblvar.GMAT_TO_GRE[int(each[0])] = int(each[1])

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

_load_convert_rule() # 加载一些常用的分数换算规则

_load_base_info() # 加载一些表的信息（institute_info, major_info）

_load_interface_methods() # 接口调用的方法 eg:{方法名：方法参数}

get_default_target_school_score() # 目标档次学校的gpa、toefl\ielts、gre\gmat的分数要求'

get_avg_score_by_offer() # 根据major_id返回关联申请成功的案例offer的平均成绩