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
        'credential': {
            'level':  100,#默认值
        },
        'competition': {
            'level':  100,#默认值
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
    result = assess_applier(test_dict, 'finance')  # law是目标文件的文件名
    print(u"最终返回的dict是：")
    print(result['result'])
    print(u"该学生的得分是：" + str(result['score']))
    print(u"该学生的分级结果是：" + str(result['level']))
