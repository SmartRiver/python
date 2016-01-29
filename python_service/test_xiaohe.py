# -*- coding: utf-8 -*-
__author__ = 'Elliot'
import subprocess
from select_school import assess_applier
import json

if __name__ == "__main__":

    test_dict = {
        'gpa': 3.7,
        'current-school':8,
        'toefl': {
            'total': 103,
            'speaking': 25,
        },
        'ielts': {
            'total': 7,
        },
        'gre': {
            'total': 327,
            'v': 157,
        },
        'research': {
            'duration': 3,  # 0-99h
            'level': 0,  # 国家级实验室 or 国家重点项目
            'achievement': 0,  # SCI一作
            'recommendation': 1,  # 是，讲师级别的推荐信
        },
        'work': {
            'duration': 4,  # 无
            'level': 0,  # 默认
            'recommendation': 0,  # 默认
        },
        'internship': {
            'duration': 7,  # 无
            'level': 0,  # 默认
            'recommendation': 0,  # 默认
        },
        'scholarship': {
            'level': 2,  # 校级一等奖
        },
        'activity': {
            'duration': 2,
            'type': 2,  #
        },
        'credential': {
            'level': 1,  # 默认值
        },
        'competition': {
            'level':  3,  # 默认值
        },
     }
    list = ['accounting', 'ce', 'environment', 'pr', 'me', 'general', 'journalism', 'marketing', 'finance', 'cs', 'economics', 'biology', 'law', 'mis', 'tesol', 'materials']
    for each in ['law']:
        print each
        result = assess_applier(test_dict, each)
        print u"最终返回的dict是："
        print json.dumps(result, indent=4)
        print '\n\n\n'
