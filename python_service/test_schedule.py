# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'

from schedule import schedule
import json
from translator import *
if __name__ == "__main__":

    ori_condition = {
        'gpa': 3.7,
        'current-school': 8,
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
    orig_condition = {
        'major': '法学',
        'grade': '大三',  # 【'大一','大二','大三','大四'】
        'target_level': 1,  # 表示目标院校档次，1-4分别表示TOP10,TOP20-30,TOP30-50,TOP50-100
        'gpa': '3.8-3.9/90-93',
        'current-school': '海外本科',
        'toefl': {
            'total': '109+/8或Waiver',
            'speaking': '26+/8+或 海本',
        },
        'gre': {
            'total': '330+/740+',
            'aw': '4.5-5',
        },
        'research': {
            'duration': '1年-2年',  # 0-99h
            'level': '海外实验室or重点项目',  # 国家级实验室 or 国家重点项目
            'achievement': '国内期刊',  # SCI一作
        },
        'internship': {
            'duration': '3-6个月',  # 无
            'level': '国内知名企业',  # 默认
            'recommendation': '直属领导推荐',  # 默认
        },
        'scholarship': {
            'level': '校一等奖学金',  # 校级一等奖
        },
        'activity': {
            'duration': '3-6个月',
            'type': '国内志愿者',  #
        },
        'competition': {
            'level':  '国家级奖项',  # 默认值
        },
    }

    condition = translateFromFrontToBack(orig_condition)

    grade = '‘大二’'
    target_level = 1

    print condition
    print '_______'

    result = schedule(condition)
    #输出结果
    print json.dumps(result, indent=4)
