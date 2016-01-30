# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'
__doc__ = '''this py is used to schedule the timetable for those who want to study abroad,
                the input is the grade、 target school level、 condition of the user，
                the output is the schedule describing what they should prepare in different term'''
import json
import time

# 每个部分目标值
SEG_TARGET_DICT = {}

# 大一到大四13个时间段每个时间段可以完成的目标
TERM_NODE_DICT = {}

# 初始化目标内容集合
NODE_LIST = list()

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

def schedule(condition, grade='大一', target_level=2):
    grade = get_start_term(grade)
    return_dict = {}
    print 'grade %d ' % grade
    print TERM_NODE_DICT[grade]
    if 1 <= grade <= 7:
        node_temp_dict = eval(TERM_NODE_DICT[grade])
        for each in node_temp_dict:
            node_temp_dict[each] = node_filter(condition, node_temp_dict[each], target_level)

    return_dict['grade'] = grade
    return_dict['schedule'] = node_temp_dict
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
    for each in open('resource/schedule/schedule.csv', 'r').readlines():
        if each[0] == '#':
            continue
        each = each.strip('\r').strip('\n')
        TERM_NODE_DICT[int(each[:2])] = each[3:]

__init__()
