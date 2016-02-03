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
            'duration': 3,
            'level': 0,
            'achievement': 0,
            'recommendation': 1,
        },
        'work': {
            'duration': 4,
            'level': 0,
            'recommendation': 0,
        },
        'internship': {
            'duration': 7,
            'level': 0,
            'recommendation': 0,
        },
        'scholarship': {
            'level': 2,
        },
        'activity': {
            'duration': 2,
            'type': 2,
        },
        'credential': {
            'level': 1,
        },
        'competition': {
            'level':  3,
        },
     }


    ttt = {
        'major': '法学',
        'grade': '大二',
        'target_level': '4',
        'gpa': '3.8-3.9/90-93',
        'current-school': '海外本科',
        'toefl': {
            'total': '109+/8或Waive',
            'speaking': '26+/8+或 海本',
        },
        'gre': {
            'total': '330+/740+',
            'aw': '4.5-5',
        },
        'research': {
            'duration': '1年-2年',
            'level': '海外实验室or重点项目',
            'achievement': '国内期刊',
        },
        'internship': {
            'duration': '3-6个月',
            'level': '国内知名企业',
            'recommendation': '直属领导推荐',
        },
        'scholarship': {
            'level': '校一等奖学金',
        },
        'activity': {
            'duration': '3-6个月',
            'type': '国内志愿者',
        },
        'competition': {
            'level':  '国家级奖项',
        },
    }
    orig_condition = {
        'major': '法学',
        'grade': '大二',  # 【'大一','大二','大三','大四'】
        'target_level': '4',  # 表示目标院校档次，1-4分别表示TOP10,TOP20-30,TOP30-50,TOP50-100
        'gpa': '',
        'current-school': '',
        'toefl': {
            'total': '',
            'speaking': '26+/8+或 海本',
        },
        'gre': {
            'total': '',
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
            'level':  '',  # 默认值
        },
    }
    condition = {}
    #condition = translateFromFrontToBack(orig_condition)


    grade = '‘大二’'
    target_level = 1

    #print condition
    print '_______'

    result = schedule(orig_condition)
    #输出结果
    print json.dumps(result, ensure_ascii=False, indent=4)
