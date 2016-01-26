# -*- coding: utf-8 -*-
__author__ = 'Elliot'
import subprocess
from select_school import assess_applier
import json

if __name__ == "__main__":

    test_dict = {
        'gpa': 3,
        'toefl': {
            'total': 100,
            'speaking': 25,
        },
        'ielts': {
            'total': 7,
        },
        'gre': {
            'total': 320,
            'v': 153,
        },
        'research': {
            'duration': 6,  # 0-99h
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
            'level': 4,  # 校级一等奖
        },
        'activity': {
            'duration': 0,
            'type': 0,  #
        },
        'credential': {
            'level':  100,#默认值
        },
        'competition': {
            'level':  100,#默认值
        },
        'credential': {
            'level': 100,#默认值
        },
     }
    list = ['cs', 'ce', 'environment', 'pr', 'me', 'general', 'journalism', 'marketing', 'finance', 'accounting', 'economics', 'biology', 'law', 'mis', 'tesol', 'materials']
    for each in list:
        print each
        result = assess_applier(test_dict, each)
        print u"最终返回的dict是："
        print json.dumps(result, indent=4)
        print '\n\n\n'
