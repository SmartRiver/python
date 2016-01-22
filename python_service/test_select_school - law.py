# -*- coding: utf-8 -*-
__author__ = 'Elliot'
import subprocess
from select_school_debug import assess_applier
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
    }
    result = assess_applier(test_dict, 'law_debug')  # law是目标文件的文件名
    print(u"最终返回的dict是：")
    print(result['result'])
    print(u"该学生的得分是：" + str(result['score']))
    print(u"该学生的分级结果是：" + str(result['level']))
