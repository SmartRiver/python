# -*- coding: utf:-8 -*-
__author__ = 'Elliot'
import os
import re
import copy
import json
import logging
from translator import *
from common_func import exit_error_func


def get_value(aim_dict, equation_unit):
    # 如果是用户输入的成绩，则取出来
    if equation_unit[0] == '%':
        equation_unit = equation_unit[1:]
        # 如果包含子字段
        if equation_unit.find('*') > -1:
            father_key = equation_unit.split('*')[0]
            child_key = equation_unit.split('*')[1]
            if father_key in aim_dict:
                if child_key in aim_dict[father_key]:
                    return float(aim_dict[father_key][child_key])
                elif father_key+'-'+child_key in DEFAULT_SEG_DICT:
                    return float(DEFAULT_SEG_DICT[father_key+'-'+child_key])
                else:
                    return 'false'
            elif father_key+'-'+child_key in aim_dict:
                return float(aim_dict[father_key+'-'+child_key])
            elif father_key+'-'+child_key in DEFAULT_SEG_DICT:
                return float(DEFAULT_SEG_DICT[father_key+'-'+child_key])
            else:
                return 'false'
        else:
            try:
                if equation_unit in aim_dict:
                    return float(aim_dict[equation_unit])
                elif equation_unit in DEFAULT_SEG_DICT:
                    return float(DEFAULT_SEG_DICT[equation_unit])
                elif equation_unit == 'reletter':
                    return 0.0
                else:
                    return 'false'
            except:
                logging.error('wrong : ' + equation_unit)
    else:
        try:
            res = float(equation_unit)
            return res
        except:
            return 'false'

def execute_equation(origin_dict, equation):
    equation = equation.split('//')[0]
    # 去除末尾的\r
    if equation[-1] == '\r':
        equation = equation[:-1]
    unit_list = filter(
        lambda x: x != '',
        re.split(r'[,\t]', equation)
    )
    if len(unit_list) <= 2:
        return False
    out_prop, equation_type = unit_list[0], unit_list[1]
    if out_prop == 'reletter':
        return False
    num_list = map(
        lambda x: get_value(origin_dict, x),
        unit_list[2:]
    )
    # 如果没有输入某个维度的分数，则返回
    if 'false' in num_list:
        return False
    if equation_type == 'range':
        if num_list[3] > num_list[1] >= num_list[2]:
            logging.warn('[match] - success : '+equation)
            origin_dict[out_prop] = num_list[0]
            global LEVEL_SEGMENT_DICT
            LEVEL_SEGMENT_DICT[out_prop] = int(unit_list[6])
            return True
        else:
            return False
    elif equation_type == 'max':
        origin_dict[out_prop] = max(num_list)
        return True
    elif equation_type == 'min':
        origin_dict[out_prop] = min(num_list)
        return True
    elif equation_type == 'sum':
        if out_prop == 'result':
            global seg_set
            seg_set = set(map(lambda x: x.strip('%'), unit_list[2:]))
        try:
            origin_dict[out_prop] = sum(num_list)
        except:
            logging.error('something is wrong when executing :'+out_prop)
            logging.error(equation)
        return True
    elif equation_type == 'multi':
        temp_result = 1
        try:
            for num in num_list:
                temp_result *= num
        except:
            logging.error('something is wrong when executing :'+out_prop)
            logging.error(equation)
        origin_dict[out_prop] = temp_result
        return True
    else:
        return False
# 用户每个部分分数等级，从1开始
LEVEL_SEGMENT_DICT = {}
# 每个专业的评估规则
ASSESS_RULE_DICT = {}
# 六维的各个维度满分的字典、二维
FULL_SCORE_DICT = {}
# 每个专业的维度
seg_set = set()
# 每个专业不包含的模块seg
STOP_SEG_DICT = {}
# 每个部分的默认值
DEFAULT_SEG_DICT = {}

# author:xiaohe
# 六维各维度得分计算
def get_seg_score(result, type):
    set_dict = {
        'gpa': 0.0,
        'language': 0.0,
        'gre': 0.0,
        'work': 0.0,
        'research': 0.0,
        'other': 0.0,
    }
    # 六维中的其它，由以下六个部分组成
    other_seg = ('activity', 'scholarship', 'credential', 'competition')

    if 'work' in result:
        set_dict['work'] = round(float(result['work']), 1)
    if 'research' in result:
        set_dict['research'] = round(float(result['research']), 1)

    for each in seg_set:
        if each == 'gpa':
            set_dict['gpa'] = round(float(result['gpa']), 1)
        elif each == 'language':
            set_dict['language'] = round(float(result['language']), 1)
        elif each == 'gre':
            set_dict['gre'] = round(float(result['gre']), 1)
        elif each in other_seg:
            set_dict['other'] = round(float(result[each])+set_dict['other'], 1)
    return set_dict

# author:xiaohe
# 增加一个返回百分制的能力值
level_dict = {
    'accounting': '6-180',
    'law': '7-125',
    'marketing': '7-160',
    'mis': '6-170',
    'pr': '4-130',
    'tesol': '4-120',
    'cs': '10-150',
    'economics': '8-125',
    'finance': '8-175',
    'journalism': '5-130',
    'biology': '8-150',
    'ce': '8-150',
    'environment': '7-145',
    'materials': '7-155',
    'me': '7-155',
    'general': '7-130',
}
def display_value(score, level, major_type):
    levels = int(level_dict[major_type].split('-')[0])
    base_score = int(level_dict[major_type].split('-')[1])
    extra = round(score/base_score * 3, 1)
    base = 80
    if 3 < levels <= 5:
        baseline = 70 - (levels-5)*5
        base = baseline + (levels-level)*4
    elif 5 < levels <= 8:
        baseline = 65 - (levels-6)*4
        base = baseline + (levels-level)*5
    elif 8 < levels:
        baseline = 50 - (levels-9)*3
        base = baseline + (levels-level)*5

    value = base+float(extra)
    value = 99.0 if value > 99.0 else value
    return value

def get_segment_level():
    global LEVEL_SEGMENT_DICT
    seg_level_dict = {
        'gpa-score-level': 'gpa-score',
        'gpa-school-level': 'gpa-school',
        'toefl-level': 'toefl-base',
        'ielts-level': 'ielts-base',
        'gre-base-level': 'gre-base',
        'gre-aw-level': 'gre-aw',
        'gmat-base-level': 'GMAT-base',
        'gmat-aw-level': 'GMAT-writing',
        'research-duration-level': 'research-duration',
        'research-level-level': 'research-level',
        'research-achievement-level': 'research-achievement',
        'research-level': 'research-factor',
        'work-duration-level': 'work-duration',
        'work-level-level': 'work-level',
        'work-level': 'work-factor',
        'internship-duration-level': 'internship-duration',
        'internship-level-level': 'internship-level',
        'internship-level': 'internship-factor',
        'activity-duration': 'activity-duration',
        'activity-type': 'activity-type',
        'activity-level': 'activity-factor',
        'competition-level': 'competition-level',
        'scholarship-level': 'scholarship-level',
        'credential-level': 'credential-level',
        'result-level': 'level',
    }
    return_level_dict = dict()
    for key in seg_level_dict:
        if seg_level_dict[key] in LEVEL_SEGMENT_DICT:
            return_level_dict[key] = LEVEL_SEGMENT_DICT[seg_level_dict[key]]

    return return_level_dict
# 去除用户请求里专业不存在的字段
def remove_stop_seg(temp_dict, rule_type):
    for each in STOP_SEG_DICT[rule_type]:
        if each in temp_dict:
            del temp_dict[each]

def __init__():
    list_dirs = os.walk('resource/assess_rule')
    for root, dirs, files in list_dirs:
        for f in files:
            rule_path = os.path.join(root, f)
            if f[0:f.rfind('.')] != 'value':
                rule_type = f[0:f.rfind('.')]
                ASSESS_RULE_DICT[rule_type] = map(
                lambda x: x.replace('\n', ''),
                file(rule_path).readlines()
                )
            else:
                for each in open(rule_path).readlines():
                    each = each.strip('\r').strip('\n')
                    each_list = each.split(',')
                    if each_list[1] == 'stop':
                        STOP_SEG_DICT[each_list[0]] = list()
                        for each_stop in each.split(',')[2:]:
                            STOP_SEG_DICT[each_list[0]].append(each_stop)
                    elif each_list[1] == 'default':
                        DEFAULT_SEG_DICT[each_list[2]] = float(each_list[3])
                    else:
                        if str(each_list[0]) in FULL_SCORE_DICT:
                            FULL_SCORE_DICT[str(each_list[0])].update({str(each_list[1]): int(each_list[2])})
                        else:
                            FULL_SCORE_DICT.update({str(each_list[0]): {str(each_list[1]): int(each_list[2])}})
RULE_TYPE_DICT = {
    u'市场营销': 'marketing',
    u'金融学': 'finance',
    u'会计学': 'accounting',
    u'信息管理系统': 'mis',
    u'计算机科学与技术': 'cs',
    u'公共关系': 'pr',
    u'新闻媒体': 'journalism',
    u'经济学': 'economics',
    u'对外英语教学': 'tesol',
    u'化学工程': 'ce',
    u'电子电机工程': 'ee',
    u'机械工程': 'me',
    u'环境工程': 'environment',
    u'土木工程': 'civil',
    u'材料': 'materials',
    u'生物': 'biology',
    u'法学': 'law',
    u'数学': 'math',
    u'物理': 'physics',
}

def assess_applier(applier_dict):
    rule_type = applier_dict['major']
    rule_type = rule_type.strip('\r').strip('\n').replace(r'"', '').replace('\'', '')

    if len(str(applier_dict['gpa'])) > 5:
        try:
            temp_dict = translateFromFrontToBack(applier_dict)
            if len(temp_dict['mismatch']) == 0:
                temp_dict = temp_dict['result']
            else:
                return exit_error_func(u'转换出错参数列表:'+str(temp_dict['mismatch']), 1)
        except:
            return exit_error_func(u'转换参数出错:'+str(applier_dict), 1)

    else:
        temp_dict = applier_dict.copy()
    if rule_type in RULE_TYPE_DICT:
        rule_type = RULE_TYPE_DICT[rule_type]

    if rule_type not in ASSESS_RULE_DICT:
        rule_type = 'general'

    remove_stop_seg(temp_dict, rule_type)

    for equation in ASSESS_RULE_DICT[rule_type]:
        is_successful = execute_equation(temp_dict, equation)

    try:
        display_score = display_value(temp_dict['result'], int(temp_dict['level']), rule_type)
    except:
        try:
            base_score = int(level_dict[rule_type].split('-')[1])
            display_score = temp_dict['result']/base_score * 100
        except:
            return exit_error_func(applier_dict, 3)
    display_score = 99.0 if display_score > 99.0 else display_score

    score = round(float(temp_dict['result']), 1)
    seg_score = get_seg_score(temp_dict.copy(), rule_type)

    return_dict = {}
    return_dict = {
        'level': get_segment_level(),
        'score': score,
        'result_level': LEVEL_SEGMENT_DICT['level'],
        'display_score': display_score,
        'seg_full_score': FULL_SCORE_DICT[rule_type],
        'seg_score': seg_score,
    }

    try:
        return return_dict
    except:
        return exit_error_func(applier_dict, 3)

__init__()

