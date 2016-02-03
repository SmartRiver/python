# -*- coding: utf-8 -*-
__author__ = 'Elliot'
import os
import re
import copy
from translator import *
from common_func import exit_error_func

def get_value(aim_dict, equation_unit):
    if equation_unit[0] == '%':
        temp_value = aim_dict
        for aim_prop in equation_unit[1:].split('*'):
            try:
                temp_value = temp_value[aim_prop]
            except:
                temp_value = 1.0
        #print 'get_value:'
        #print aim_dict
        return temp_value
    else:
        try:
            res = float(equation_unit)
        except:
            res = equation_unit
    return res

def execute_equation(origin_dict, equation):
    equation = equation.split('//')[0]
    # 去除末尾的\r
    if equation[-1] == '\r':
        equation = equation[:-1]
    unit_list = filter(lambda x: x != '', re.split(r'[,\t]', equation))
    if len(unit_list) <= 2:
        return False
    out_prop, equation_type = unit_list[0], unit_list[1]
    num_list = map(
        lambda x: get_value(origin_dict, x),
        unit_list[2:]
    )
    if equation_type == 'range':
        if num_list[3] > num_list[1] >= num_list[2]:
            origin_dict[out_prop] = num_list[0]
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
            seg_set = set(map(lambda x : x.strip('%'),unit_list[2:]))
            try:
                origin_dict[out_prop] = sum(num_list)
            except:
                print 'something is wrong when executing :'
                print equation
                print 'wrong item: ' + out_prop
                return True
    elif equation_type == 'multi':
        temp_result = 1
        try:
            for num in num_list:
                temp_result *= num
        except:
            print 'something is wrong when executiing :'
            print equation
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
def get_seg_score(result,type):
    set_dict = {'gpa':0.0,'language':0.0,'gre':0.0,'work':0.0,'research':0.0,'other':0.0}
    if 'work' in result:
        try:
            set_dict['work'] = round(float(result['work']),1)
        except:
            print 'something is wrong when calculate the work vaule of ' + type
            print result['work']
    if 'research' in result:
        try:
            set_dict['research'] = round(float(result['research']),1)
        except:
            print 'something is wrong when calculate the research value of  ' + type
            print result['research']

    for each in seg_set:
        if each == 'gpa':
            set_dict['gpa'] = round(float(result['gpa']),1)
        elif each == 'language':
            set_dict['language'] = round(float(result['language']),1)
        elif each == 'gre':
            set_dict['gre'] = round(float(result['gre']),1)
        elif each != 'work-research':
            set_dict['other'] = round(float(result[each])+set_dict['other'],1)
    return set_dict

# author:xiaohe
# 增加一个返回百分制的能力值
level_dict = {
    u'accounting':'6-175',
    u'law':'7-135',
    u'marketing':'7-160',
    u'mis':'6-170',
    u'pr':'4-125',
    u'tesol':'4-110',
    u'cs':'10-150',
    u'economics':'8-100',
    u'finance':'8-195',
    u'journalism':'5-125',
    u'biology':'8-135',
    u'ce':'8-135',
    u'environment':'7-130',
    u'materials':'7-135',
    u'me':'7-135',     
    u'general':'7-135',
}
def display_value(score, level, type):
    levels = int(level_dict[type].split('-')[0])
    base_score = int(level_dict[type].split('-')[1])
    extra = score/base_score * 3
    extra = str(extra).split('.')[0]+'.'+str(extra).split('.')[1][:1]
    base = 80
    if 3 < levels <= 5:
        baseline = 70 - (levels-5)*5
        base = baseline + (levels-level)*4
    elif 5 < levels <=8:
        baseline = 65 - (levels-6)*4
        base = baseline + (levels-level)*5
    elif 8 < levels:
        baseline = 50 - (levels-9)*3
        base = baseline + (levels-level)*5

    value = base+float(extra)
    value = 99.0 if value > 99.0 else value
    return value

def __init__():
    list_dirs = os.walk('resource/assess_rule')
    for root, dirs, files in list_dirs:
        for f in files:
            rule_path = os.path.join(root,f)
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
    print 'before . . . '
    print 'current-school: '+ applier_dict['current-school']
    print json.dumps(applier_dict, indent=4)

    temp_dict = {}
    if len(str(applier_dict['gpa'])) > 5:
        if rule_type == '法学' or rule_type == 'law':
            applier_dict['major'] = '法学'
        temp_dict = translateFromFrontToBack(applier_dict)
        try:
            temp_dict = translateFromFrontToBack(applier_dict)
            if len(temp_dict['mismatch']) == 0:
                temp_dict = temp_dict['result']
            else:
                return exit_error_func(u'转换出错参数列表:'+str(temp_dict['mismatch']), 1)
        except Exception, e:
            return exit_error_func(u'转换参数出错:'+str(applier_dict), 1)

    else:
        temp_dict = applier_dict.copy()
    print 'after . . . '
    print json.dumps(temp_dict, indent=4)
    print 'current-school: '+ str(temp_dict['current-school'])
    if rule_type in RULE_TYPE_DICT:
        rule_type = RULE_TYPE_DICT[rule_type]
    
    if rule_type not in ASSESS_RULE_DICT:
        rule_type = 'general'
    for equation in ASSESS_RULE_DICT[rule_type]:
        is_successful = execute_equation(temp_dict, equation)
    
    try:
        display_score = display_value(temp_dict['result'],int(temp_dict['level']),rule_type)
    except:
        base_score = int(level_dict[rule_type].split('-')[1])
        display_score = temp_dict['result']/base_score *100
        display_score = 99.0 if display_score > 99.0 else display_score

    score = round(float(temp_dict['result']), 1)
    seg_score = get_seg_score(temp_dict.copy(), rule_type)

    return {
        'display_score':display_score,
        'score': float(score),
        'level': int(temp_dict['level']),
        #'result': temp_dict,
        'seg_full_score': FULL_SCORE_DICT[rule_type],
        'seg_score':seg_score,
    }

__init__()

