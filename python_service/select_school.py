# -*- coding: utf:-8 -*-
__author__ = 'Elliot'
import os
import re
import copy
import json

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
                    print '11-- in aim_dict'
                    print equation_unit
                    return float(aim_dict[father_key][child_key])
                elif father_key+'-'+child_key in DEFAULT_SEG_DICT:
                    print '11-- default'
                    print equation_unit
                    return float(DEFAULT_SEG_DICT[father_key+'-'+child_key])
                else:
                    print '11-- false'
                    print equation_unit
                    return 'false'
            elif father_key+'-'+child_key in aim_dict:
                return float(aim_dict[father_key+'-'+child_key])
            elif father_key+'-'+child_key in DEFAULT_SEG_DICT:
                print 'use default 12'
                print equation_unit + '-' + father_key+'-'+child_key
                return float(DEFAULT_SEG_DICT[father_key+'-'+child_key])
            else:
                print '12 -- false'
                return 'false'
        else:
            try:
                if equation_unit in aim_dict:
                    print '22-in aim_dict'
                    print equation_unit
                    return float(aim_dict[equation_unit])
                elif equation_unit in DEFAULT_SEG_DICT:
                    print 'use default2'
                    print equation_unit
                    return float(DEFAULT_SEG_DICT[equation_unit])
                elif equation_unit == 'reletter':
                    return 0.0
                else:
                    print '22 -- false'
                    print equation_unit
                    return 'false'
            except:
                print 'wrong : ' + equation_unit
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
    print num_list
    # 如果没有输入某个维度的分数，则返回
    if 'false' in num_list:
        print '----False in get_value'
        print equation
        return False
    if equation_type == 'range':
        if num_list[3] > num_list[1] >= num_list[2]:
            print '匹配成功'+equation
            origin_dict[out_prop] = num_list[0]
            if 'gpa-score' in origin_dict:
                print 'success'
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
def get_seg_score(result, type):
    set_dict = {
        u'gpa': 0.0,
        u'language': 0.0,
        u'gre': 0.0,
        u'work': 0.0,
        u'research': 0.0,
        u'other': 0.0,
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
            print 'other:' + each + '\t' + str(result[each])
            set_dict['other'] = round(float(result[each])+set_dict['other'], 1)
    return set_dict

# author:xiaohe
# 增加一个返回百分制的能力值
level_dict = {
    u'accounting': '6-180',
    u'law': '7-125',
    u'marketing': '7-160',
    u'mis': '6-170',
    u'pr': '4-130',
    u'tesol': '4-120',
    u'cs': '10-150',
    u'economics': '8-125',
    u'finance': '8-175',
    u'journalism': '5-130',
    u'biology': '8-150',
    u'ce': '8-150',
    u'environment': '7-145',
    u'materials': '7-155',
    u'me': '7-155',
    u'general': '7-130',
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
        u'gpa-score-level': 'gpa-score',
        u'gpa-school-level': 'gpa-school',
        u'toefl-level': 'toefl-base',
        u'ielts-level': 'ielts-base',
        u'gre-base-level': 'gre-base',
        u'gre-aw-level': 'gre-aw',
        u'gmat-base-level': 'GMAT-base',
        u'gmat-aw-level': 'GMAT-writing',
        u'research-duration-level': 'research-duration',
        u'research-level-level': 'research-level',
        u'research-achievement-level': 'research-achievement',
        u'research-level': 'research-factor',
        u'work-duration-level': 'work-duration',
        u'work-level-level': 'work-level',
        u'work-level': 'work-factor',
        u'internship-duration-level': 'internship-duration',
        u'internship-level-level': 'internship-level',
        u'internship-level': 'internship-factor',
        u'activity-duration': 'activity-duration',
        u'activity-type': 'activity-type',
        u'activity-level': 'activity-factor',
        u'competition-level': 'competition-level',
        u'scholarship-level': 'scholarship-level',
        u'credential-level': 'credential-level',
        u'result-level': 'level',
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

def assess_applier(applier_dict, rule_type):
    # display default dict
    for each in DEFAULT_SEG_DICT:
        print each + str(DEFAULT_SEG_DICT[each])
    temp_dict = applier_dict.copy()
    # print json.dumps(temp_dict,indent=4)
    remove_stop_seg(temp_dict, rule_type)
    # print json.dumps(temp_dict,indent=4)
    if rule_type not in ASSESS_RULE_DICT:
        rule_type = 'general'
    for equation in ASSESS_RULE_DICT[rule_type]:
        is_successful = execute_equation(temp_dict, equation)
    
    try:
        display_score = display_value(temp_dict['result'], int(temp_dict['level']), rule_type)
    except:
        base_score = int(level_dict[rule_type].split('-')[1])
        display_score = temp_dict['result']/base_score * 100
    display_score = 99.0 if display_score > 99.0 else display_score
    
    score = round(float(temp_dict['result']), 1)
    seg_score = get_seg_score(temp_dict.copy(), rule_type)

    return {
        'level': get_segment_level(),
        'score': score,
        'result_level': LEVEL_SEGMENT_DICT['level'],
        'display_score': display_score,
        'seg_full_score': FULL_SCORE_DICT[rule_type],
        'seg_score': seg_score,
    }

__init__()

