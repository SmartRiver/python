#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from global_variable import (GPA_SCHOOL_LEVEL, SELECT_SCHOOL_TARGET_SCORE, SELECT_SCHOOL_OFFER_SCORE, INSTITUTE_ID_TO_NAME_EN, INSTITUTE_ID_TO_NAME_ZH, INSTITUTE_ID_TO_LOCATION, INSTITUTE_MAJOR_LEVEL)
from common_func import (convert_var_type, exit_error_func)
__author__  = 'johnson'
__doc__     = '''this script is used to match schools for student by assess the score of them'''

DATA_TEMPLATE = {"major":8,"gpa":{"score":"3.5","school":"双非二本"},"gmat":{"total":"0","writing":"0"},"gre":{"total":"328","writing":"4"},"toefl":{"total":"106","speaking":"25"},"ielts":{"total":"0","speaking":"0"}}


def evaluate_gpa(gpa_score, gpa_school=12):
    '''根据学校的本科学校档次不同，乘上一个系数'''
    gpa_school = convert_var_type(gpa_school, 'int')
    if gpa_school not in GPA_SCHOOL_LEVEL:
        raise KeyError('不包含该学校档次{}'.format(gpa_school))
    gpa_score = convert_var_type(gpa_score, 'float')
    return '{:.2f}'.format(gpa_score*GPA_SCHOOL_LEVEL[gpa_school])

def _student_data_check(student_data):
    '''检查用户数据是否完整、合法'''
    for first_key in DATA_TEMPLATE:
        if first_key not in student_data:
            raise KeyError('缺乏{0}数据，第一层键名为{0}'.format(first_key))
        if first_key == 'major':
            continue
        for second_key in DATA_TEMPLATE[first_key]:
            if second_key not in student_data[first_key]:
                raise KeyError('缺乏{0}的{1}数据，第二层键名为[{0}][{1}]'.format(first_key, second_key))

def _get_student_level(student_data, _temp_list, _major):
    '''根据学生三围成绩划分档次'''
    _temp_level = {
        'gpa'   : 5,
        'toefl_total' : 5,
        'ielts_total' : 5,
        'gre_total'   : 5,
        'gmat_total'  : 5,
    }
    
    for each in SELECT_SCHOOL_TARGET_SCORE[_major]:
        for score_key, score_value in _temp_list.items():
            if convert_var_type(score_value, 'float') > SELECT_SCHOOL_TARGET_SCORE[_major][each][score_key]:
                if _temp_level[score_key] > each:
                    _temp_level.update({score_key: each})


    _res_level = {
        'gpa' : _temp_level['gpa'],
        'it'  : min(_temp_level['toefl_total'], _temp_level['ielts_total']),
        'gg'  : min(_temp_level['gmat_total'], _temp_level['gre_total']),
    }

    return max(_res_level.values())

def _get_return_institute(qualified_institute, _target_level, _major):
    '''按需求格式返回选校结果'''
    _guarantee_institute    = []
    _sprint_institute       = []
    _suit_institute       = []
    for each in qualified_institute:
        _temp_res = {
            'id': each,
            'name_en': INSTITUTE_ID_TO_NAME_EN[each],
            'name_zh': INSTITUTE_ID_TO_NAME_ZH[each],
            'location_type': INSTITUTE_ID_TO_LOCATION[each]
        }
        if _target_level == 1:
            if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
                _suit_institute.append(_temp_res)
            elif each in INSTITUTE_MAJOR_LEVEL[_major][_target_level+1]:
                _guarantee_institute.append(_temp_res)
        elif _target_level == 4:
            if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
                _suit_institute.append(_temp_res)
        else:
            if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
                _suit_institute.append(_temp_res)
            elif each in INSTITUTE_MAJOR_LEVEL[_major][_target_level+1]:
                _guarantee_institute.append(_temp_res)
    
    for each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
        if each not in qualified_institute:
            _sprint_institute.append({
                    'id': each,
                    'name_en': INSTITUTE_ID_TO_NAME_EN[each],
                    'name_zh': INSTITUTE_ID_TO_NAME_ZH[each],
                    'location_type': INSTITUTE_ID_TO_LOCATION[each]
                })
    return {
        'status':'success',
        'result':{
            'level': _target_level,
            'guarantee': _guarantee_institute,
            'sprint': _sprint_institute,
            'suit': _suit_institute
        }
    }


def assess_single(**condition):
    '''按照学生成绩匹配确切的院校'''
    student_data = condition['condition']
    print(student_data)
    _student_data_check(student_data)
    gpa = evaluate_gpa(student_data['gpa']['score'], student_data['gpa']['school'])

    if convert_var_type(student_data['ielts']['total'], 'int') == 0 and convert_var_type(student_data['toefl']['total'], 'int') == 0:
        raise ValueError('雅思/托福 总分都没有')
    if convert_var_type(student_data['gre']['total'], 'int') == 0 and convert_var_type(student_data['gmat']['total'], 'int') == 0:
        raise ValueError('GRE/GMAT 总分都没有')

    _temp_list = {
        'gpa'           : gpa, 
        'ielts_total'   : student_data['ielts']['total'],
        'toefl_total'   : student_data['toefl']['total'], 
        'gre_total'     : student_data['gre']['total'],
        'gmat_total'    : student_data['gmat']['total'],
    }

    _major = convert_var_type(student_data['major'], 'int')
    if _major not in SELECT_SCHOOL_TARGET_SCORE:
        _major = -1
    _target_level = _get_student_level(student_data, _temp_list, _major)

    qualified_institute = []
    for each_institute in SELECT_SCHOOL_OFFER_SCORE[_major]:
        _temp_level = {
        'gpa'   : 0,
        'toefl_total' : 0,
        'ielts_total' : 0,
        'gre_total'   : 0,
        'gmat_total'  : 0,
        }
        for each_element in _temp_level:
            _temp = SELECT_SCHOOL_OFFER_SCORE[_major][each_institute][each_element]
            if _temp < 0.1:
                continue
            if float(_temp_list[each_element]) > _temp:
                _temp_level[each_element] = 1
        # 判断是否达到该院校分数要求
        if _temp_level['gpa'] == 1:
            if (_temp_level['toefl_total'] + _temp_level['ielts_total']) >= 1:
                if (_temp_level['gre_total'] + _temp_level['gmat_total']) >= 1:
                    qualified_institute.append(each_institute)
    try:
        return _get_return_institute(qualified_institute, _target_level, _major)
    except Exception as e:
        return exit_error_func(3, str(e))
    
    








