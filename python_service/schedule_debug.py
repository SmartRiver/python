# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'
__doc__ = '''this py is used to schedule the timetable for those who want to study abroad,
                the input is the grade、 target school level、 condition of the user，
                the output is the schedule describing what they should prepare in different term'''
import json

# 每个部分目标值
SEG_TARGET_DICT = {}

# 大一到大四13个时间段每个时间段可以完成的目标
TERM_NODE_DICT = {}

def schedule():
    pass
def __init__():
    for each in open('resource/schedule/target.csv', 'r').readlines():
        each = each.strip('\r').strip('\n')
        print each
        SEG_TARGET_DICT.update({each.split(',')[0]: {str(each.split(',')[1]): float(each.split(',')[2])}})
    for each in open('resource/schedule/content.csv', 'r').readlines():
        if each[0] == '#':
            continue
        each = each.strip('\r').strip('\n')
        print each


__init__()

print json.dumps(SEG_TARGET_DICT, indent=4)
