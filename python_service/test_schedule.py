# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'

from schedule import schedule
import json
from translator import *
if __name__ == "__main__":

    ori_condition = {
        'gpa': '3.8-3.9/90-93',
        'toefl': {
            'total': '105-108/7.5',
        },
        'gre': {
            'total': '325-329/710-730',
        },
    }

    condition = translateFromFrontToBack(ori_condition)

    grade = '大三'
    target_level = 1

    print condition

    result = schedule(condition, grade, target_level)

    #输出结果

    print json.dumps(result, indent=4)
