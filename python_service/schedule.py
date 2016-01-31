# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'
__doc__ = '''this py is used to schedule the timetable for those who want to study abroad,
                the input is the grade、 target school level、 condition of the user，
                the output is the schedule describing what they should prepare in different term'''
import json
import time
from translator import *

# 每个部分目标值
SEG_TARGET_DICT = {}

# 大一到大四13个时间段每个时间段可以完成的目标
TERM_NODE_DICT = {}

# 初始化目标内容集合
NODE_LIST = list()

# 大一到大四申请后各阶段名称
TERM_NAME_DICT = {
    1: u'大一上学期',
    2: u'大一寒假',
    3: u'大一下学期',
    4: u'大一暑假',
    5: u'大二上学期',
    6: u'大二寒假',
    7: u'大二下学期',
    8: u'大二暑假',
    9: u'大三上学期',
    10: u'大三寒假',
    11: u'大三下学期',
    12: u'大三暑假',
    13: u'大四上学期',
    14: u'申请后',
}

# 获取当前时间段
def get_start_term(grade='大二'):
    # 获取当前的月份
    now_month = int(time.strftime('%m', time.localtime(time.time())))
    if 1 <= now_month <= 2:
        increase = 1
    elif 3 <= now_month <= 6:
        increase = 2
    elif 7 <= now_month <= 8:
        increase = 3
    elif 9 <= now_month <= 12:
        increase = 0
    else:
        increase = 0

    if grade == '大一':
        grade = 1 + increase
    elif grade == '大二':
        grade = 5 + increase
    elif grade == '大三':
        grade = 9 + increase
    elif grade == '大四':
        grade = 13 + increase
    else:
        grade = 1
    return grade

def node_filter(condition, nodestr, target_level=2):
    node_list = list(map(lambda x: int(x), nodestr.split('-')))
    if float(condition['gpa']) >= SEG_TARGET_DICT['gpa'][str(target_level)]:
        if 1 in node_list:
            node_list.remove(1)
    if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
        if 3 in node_list:
            node_list.remove(3)
        if 4 in node_list:
            node_list.remove(4)
    if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
        if 2 in node_list:
            node_list.remove(2)
    return node_list

def schedule(origin_condition, grade='大一', target_level=2):
    condition = translateFromFrontToBack(origin_condition)
    # print grade
    grade = grade.strip('\n').strip('\r').replace(r'"', '').replace('\'', '')
    # print grade
    grade = get_start_term(grade)
    return_dict = {}
    # print 'grade %d ' % grade
    # print TERM_NODE_DICT[grade]
    if 1 <= grade <= 7:
        num = grade
    elif grade == 8:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            num = 9
        else:
            num = 8
    elif grade == 9:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            num = 11
        else:
            num = 10
    elif grade == 10:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 15
            else:
                num = 14
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 13
            else:
                num = 12
    elif grade == 11:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 19
            else:
                num = 18
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 17
            else:
                num = 16
    elif grade == 12:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 23
            else:
                num = 22
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 21
            else:
                num = 20
    elif grade == 12:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 27
            else:
                num = 26
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
                num = 25
            else:
                num = 24
    elif grade == 14:
        num = 28
    else:
        num = 28
    node_temp_dict = eval(TERM_NODE_DICT[num])

    for each in node_temp_dict:
            node_temp_dict[each] = node_filter(condition, node_temp_dict[each], target_level)

    _schedule = {}
    _schedule_name = {}
    for each in range(grade, 15):
        _schedule[each] = node_temp_dict[str(each)]
        _schedule_name[TERM_NAME_DICT[each]] = node_temp_dict[str(each)]
    return_dict['grade'] = grade
    return_dict['grade_name'] = TERM_NAME_DICT[grade]
    return_dict['schedule'] = _schedule
    return_dict['schedule_name'] = _schedule_name

    return return_dict

def __init__():
    for each in open('resource/schedule/target.csv', 'r').readlines():
        each = each.strip('\r').strip('\n')
        # print each
        target_name = each.split(',')[0]
        target_level = str(each.split(',')[1])
        target_score = float(each.split(',')[2])
        if target_name in SEG_TARGET_DICT:
            SEG_TARGET_DICT[target_name].update({target_level: target_score})
        else:
            SEG_TARGET_DICT.update({target_name: {target_level: target_score}})
    for each in open('resource/schedule/schedule.csv', 'r', encoding='utf-8').readlines():
        if each[0] == '#':
            continue
        each = each.strip('\r').strip('\n')
        TERM_NODE_DICT[int(each[:2])] = each[3:]


__init__()
