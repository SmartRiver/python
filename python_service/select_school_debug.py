# -*- coding: utf-8 -*-
__author__ = 'Elliot'
import os
import re
import traceback


def get_value(aim_dict, equation_unit):
    if equation_unit[0] == '%':
        temp_value = aim_dict
        for aim_prop in equation_unit[1:].split('*'):
            temp_value = temp_value[aim_prop]
        return temp_value
    else:
        return float(equation_unit)


def execute_equation(origin_dict, equation):
    equation = equation.split('//')[0]
    unit_list = filter(
        lambda x: x != '',
        re.split(r'[,\t]', equation)
    )
    if len(unit_list) <= 2:
        return False
    out_prop, equation_type = unit_list[0], unit_list[1]
    num_list = map(
        lambda x: get_value(origin_dict, x),
        unit_list[2:]
    )
    if equation_type == 'range':
        if num_list[3] > num_list[1] >= num_list[2]:
            origin_dict[out_prop] = num_list[0]
            return True
        else:
            return False
    elif equation_type == 'max':
        origin_dict[out_prop] = max(num_list)
        return True
    elif equation_type == 'min':
        origin_dict[out_prop] = min(num_list)
        return True
    elif equation_type == 'sum':
        origin_dict[out_prop] = sum(num_list)
        return True
    elif equation_type == 'multi':
        temp_result = 1
        for num in num_list:
            temp_result *= num
        origin_dict[out_prop] = temp_result
        return True
    else:
        return False

ASSESS_RULE_DICT = {}


def __init__():
    list_dirs = os.walk('resource/assess_rule')
    for root, dirs, files in list_dirs:
        for f in files:
            rule_type = f[0:f.rfind('.')]
            rule_path = os.path.join(root, f)
            ASSESS_RULE_DICT[rule_type] = map(
                lambda x: x.replace('\n', ''),
                file(rule_path).readlines()
            )


def assess_applier(applier_dict, rule_type):
    temp_dict = applier_dict.copy()
    if rule_type not in ASSESS_RULE_DICT:
        rule_type = 'general'
    for equation in ASSESS_RULE_DICT[rule_type]:
        if equation.find('//break') is not -1:
            print('In executing \'' + equation + '\':')
            print('Dict state before executing:')
            print(temp_dict)
            is_successful = execute_equation(temp_dict, equation)
            print('Executing result: ' + str(is_successful))
            print('Dict state after executing:')
            print(temp_dict)
            print('\n')
        else:
            try:
                execute_equation(temp_dict, equation)
            except Exception, e:
                print('Runtime error in executing \'' + equation + '\':')
                if isinstance(e, KeyError):
                    print(e.message + ' doesn\'t not exist in current dict.')
                else:
                    traceback.print_exc()
                print('\n')
                return {
                    'score': 0,
                    'level': 0,
                    'result': temp_dict,
                }
    return {
        'score': temp_dict['result'],
        'level': int(temp_dict['level']),
        'result': temp_dict,
    }

__init__()

