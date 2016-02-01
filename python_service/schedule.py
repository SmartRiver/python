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
    1: u'大一上',
    2: u'大一寒假',
    3: u'大一下',
    4: u'大一暑假',
    5: u'大二上',
    6: u'大二寒假',
    7: u'大二下',
    8: u'大二暑假',
    9: u'大三上',
    10: u'大三寒假',
    11: u'大三下',
    12: u'大三暑假',
    13: u'大四上',
    14: u'申请后',
}

# 获取当前时间段
def get_start_term(grade=5):
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

    if grade == 1:
        grade = 1 + increase
    elif grade == 2:
        grade = 5 + increase
    elif grade == 3:
        grade = 9 + increase
    elif grade == 4:
        grade = 13 + increase
    else:
        grade = 1
    return grade

def node_filter(condition, nodestr, target_level=2):
    node_list = list(map(lambda x: int(x), nodestr.split('-')))
    if float(condition['gpa']) >= SEG_TARGET_DICT['gpa'][target_level]:
        if 1 in node_list:
            node_list.remove(1)
    if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
        if 3 in node_list:
            node_list.remove(3)
        if 4 in node_list:
            node_list.remove(4)
    if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
        if 2 in node_list:
            node_list.remove(2)
    if int(condition['current-school']) == 3:
        if 9 in node_list:
            node_list.remove(9)
        if 7 in node_list:
            node_list.remove(7)
    if condition['major'] == 'law':
        if 5 in node_list:
            node_list.remove(5)
    return node_list

def schedule(origin_condition):
    return_dict = {}
    condition = translateFromFrontToBack(origin_condition)
    # print grade
    if len(condition['toefl']['total']) < 2:
        condition['toefl']['total'] = -1
    if len(condition['gre']['total']) < 2:
        condition['gre']['total'] = -1
    if type(condition['target_level']) == int:
        target_level = condition['target_level']
    elif type(condition['target_level']) != int:
        target_level = str(condition['target_level']).strip('\n').strip('\r').replace(r'"', '').replace('\'', '')
    else:
        exit_error(1)
    # print grade
    if type(condition['grade']) == int:
        grade = get_start_term(condition['grade'])
    elif type(condition['grade']) != int:
        grade = str(condition['grade']).strip('\n').strip('\r').replace(r'"', '').replace('\'', '')
        grade = get_start_term(int(grade))
    else:
        exit_error(1)

    print 'grade %d ' % grade
    # print TERM_NODE_DICT[grade]
    if 1 <= grade <= 7:
        num = grade
    elif grade == 8:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            num = 9
        else:
            num = 8
    elif grade == 9:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            num = 11
        else:
            num = 10
    elif grade == 10:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 15
            else:
                num = 14
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 13
            else:
                num = 12
    elif grade == 11:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 19
            else:
                num = 18
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 17
            else:
                num = 16
    elif grade == 12:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 23
            else:
                num = 22
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 21
            else:
                num = 20
    elif grade == 12:
        if float(condition['toefl']['total']) >= SEG_TARGET_DICT['toefl'][target_level]:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
                num = 27
            else:
                num = 26
        else:
            if float(condition['gre']['total']) >= SEG_TARGET_DICT['gre'][target_level]:
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

    node_term_list= list()
    for each in range(grade, 15):
        node_term_list.append({'grade': each, 'term': TERM_NAME_DICT[each], 'labels': node_temp_dict[str(each)]})
    return_dict['result'] = node_term_list
    return_dict['status'] = 'success'

    return return_dict
def exit_error(error_code):
    error_dict = {
        1: '参数格式错误',
    }
    error_return = {}
    error_return['status'] = error_dict[error_code]
    return error_return


def __init__():
    for each in open('resource/schedule/target.csv', 'r').readlines():
        each = each.strip('\r').strip('\n')
        # print each
        target_name = each.split(',')[0]
        target_level = int(each.split(',')[1])
        target_score = float(each.split(',')[2])
        if target_name in SEG_TARGET_DICT:
            SEG_TARGET_DICT[target_name].update({target_level: target_score})
        else:
            SEG_TARGET_DICT.update({target_name: {target_level: target_score}})
    for each in open('resource/schedule/schedule.csv', 'r').readlines():
        if each[0] == '#':
            continue
        each = each.strip('\r').strip('\n')
        TERM_NODE_DICT[int(each[:2])] = each[3:]


__init__()
