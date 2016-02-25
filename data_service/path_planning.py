#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this py is used to schedule the timetable for those who want to study abroad,
                the input is the grade、 target school level、 condition of the user，
                the output is the schedule describing what they should prepare in different term
                柳外都成絮  栏边半是苔 多情帘燕独徘徊 应是满身花雨又归来'''

import time
import json
import os
import copy
import logging
import logging.config
from db_util import *
from common_func import exit_error_func, convert_to_str, convert_to_int, convert_to_float
import assess_student
from assess_student import assess

TARGET_LEVEL_LIST = [1, 2, 3, 4] # 目标档次学校所以档次， 1为最高档
GRADE_LEVEL_LSIT = [1, 2, 3, 4] # 年级 1、2、3、4分半代表大一、大二、大三、大四
path_plan_logger = None # 日志
PATH_PLAN_DICT = {} # 各个专业每个学期的各学习提升任务权重值
TARGET_DICT = {} # 各个档次学校的每个部分的目标值
NODE_DICT = {} # 各个学习提升任务对应数据库里NODE表的ID
NODE_PRODUCT = {} #product所属的NODE（大结点）

'''获取当前时间段(学期)'''
def get_start_term(grade=1):
    now_month = time.localtime().tm_mon # 获取当前的月份
    if 3 <= now_month <= 8:
        increase = 0
    else:
        increase = -1
    grade = grade * 2 + increase
    return grade

def pre_check(target, grade):
    target = convert_to_int(target)
    if target == False or target not in TARGET_LEVEL_LIST:
        return False
    grade = convert_to_int(grade)
    if grade == False or grade not in GRADE_LEVEL_LSIT:
        return False
    return True

def schedule(user_input):
    try:
        user_condition = assess_student.assess(user_input)['result']
    except:
        return exit_error_func(6)
    part_score_dict = {}
    if 'language_type' in user_condition:
        language_type = convert_to_str(user_condition['language_type'])
        path_plan_logger.info('language_type : %s' % language_type)
        if language_type not in ['ielts', 'toefl', 'neither']: # 用户的语言类型，neither表示两者都不
            return exit_error_func(2, '托福或者雅思分数错误')
    else:
        return exit_error_func(5, '缺乏托福或者雅思分数')

    if 'exam_type' in user_condition:
        exam_type = convert_to_str(user_condition['exam_type'])
        path_plan_logger.info('exam_type : %s' % exam_type)
        if exam_type not in ['gre', 'gmat', 'neither', 'none']:
            return exit_error_func(2, 'gre或者gmat分数错误')
    else:
        return exit_error_func(5, '缺乏GRE或者GMAT参数类型说明')

    if 'student_info' in user_condition:
        student_info = user_condition['student_info']
        if 'major' in student_info:
            major = student_info['major']
            major = convert_to_str(major)
        else:
            return exit_error_func(5, 'student_info[\'major\']')
        if 'target' in student_info:
            target = student_info['target']
        else:
            return exit_error_func(5, 'student_info[\'target\']')
        if 'grade' in student_info:
            grade = student_info['grade']
        else:
            return exit_error_func(5, 'student_info[\'grade\']')

        if not pre_check(target, grade):
            path_plan_logger.info('format of target/grade is wrong. ')
            return exit_error_func(2, 'target:'+target+', grade:'+grade)
        grade = get_start_term(convert_to_int(grade))
        target = convert_to_int(target)
        if major not in PATH_PLAN_DICT:
            major = 'general'

        if 'data' in student_info:
            user_data = student_info['data']
            try:
                part_score_dict['gpa'] = convert_to_float(user_data['gpa']['score'])
                if language_type == 'ielts':
                    part_score_dict['ielts'] = convert_to_float(user_data[language_type]['total'])
                if language_type == 'toefl':
                    part_score_dict['toefl'] = convert_to_float(user_data[language_type]['total'])
                if exam_type == 'gre':
                    part_score_dict['gre'] = convert_to_float(user_data[exam_type]['total'])
                if exam_type == 'gmat':
                    part_score_dict['gmat'] = convert_to_float(user_data[exam_type]['total'])
            except Exception as e:
                return exit_error_func(5, 'student_info[\'data\']')
        else:
            return exit_error_func(5, '学生各部分分数信息')
    else:
        return exit_error_func(5, 'student_info')

    if 'dimension' in user_condition:
        dimension = user_condition['dimension']
    else:
        return exit_error_func(5, 'dimension')

    if 'dimension_full' in user_condition:
        dimension_full = user_condition['dimension_full']
    else:
        return exit_error_func(5, 'dimension_full')

    try:
        if 'research_dimension' in dimension:
            part_score_dict['research'] = convert_to_float(dimension['research_dimension'])/convert_to_float(dimension_full['research_dimension'])
        if 'internship_dimension' in dimension:
            part_score_dict['internship'] = convert_to_float(dimension['internship_dimension'])/convert_to_float(dimension_full['internship_dimension'])
        if 'activity_dimension' in dimension:
            part_score_dict['activity'] = convert_to_float(dimension['activity_dimension'])/convert_to_float(dimension_full['activity_dimension'])
        if 'scholarship_dimension':
            part_score_dict['scholarship'] = convert_to_float(dimension['scholarship_dimension'])/convert_to_float(dimension_full['scholarship_dimension'])
        if 'credential_dimension' in dimension:
            part_score_dict['credential'] = convert_to_float(dimension['credential_dimension'])/convert_to_float(dimension_full['credential_dimension'])
        if 'competition_dimension' in dimension:
            part_score_dict['competition'] = convert_to_float(dimension['competition_dimension'])/convert_to_float(dimension_full['competition_dimension'])
    except Exception as e:
        return exit_error_func(6)

    weight_dict = copy.deepcopy(PATH_PLAN_DICT[major][grade])

    if language_type == 'ielts':
        del weight_dict['toefl']
    elif language_type == 'toefl':
        del weight_dict['ielts']
    if exam_type == 'gre':
        del weight_dict['gmat']
    elif exam_type == 'gmat':
        del weight_dict['gre']
    elif exam_type == 'none':
        del weight_dict['gmat']
        del weight_dict['gre']

    target_dict = TARGET_DICT[target]

    finished_node = []
    unfinished_node = []

    for each in weight_dict:
        if each in part_score_dict:
            if part_score_dict[each] > target_dict[each]:
                finished_node.append(NODE_DICT[each])
            else:
                ratio = (target_dict[each] - part_score_dict[each]) / target_dict[each]
                weight_dict[each] = weight_dict[each] * (1+ratio)
                unfinished_node.append(each)

    result_weight = sorted(weight_dict.items(), key=lambda x:x[1], reverse=True)

    return_node = [79,80,81,94]

    return_unfinished_node = []
    for each in result_weight:
        if each[0] in NODE_DICT:
            return_node.insert(0, NODE_DICT[each[0]])
        if each[0] in unfinished_node:
            return_unfinished_node.append(NODE_DICT[each[0]])

    # add ID of product to related NODE
    #for index,item in enumerate(finished_node):
    #    finished_node[index] = {'node_id': item, 'products': []}
    #    if item in NODE_PRODUCT:
    #        finished_node[index] = {'node_id': item, 'products': NODE_PRODUCT[item]}
    for index,item in enumerate(return_unfinished_node):
        return_unfinished_node[index] = {'node_id': item, 'products': []}
        if item in NODE_PRODUCT:
            return_unfinished_node[index] = {'node_id': item, 'products': NODE_PRODUCT[item]}
    for index,item in enumerate(return_node):
        return_node[index] = {item: []}
        if item in NODE_PRODUCT:
            return_node[index] = {item: NODE_PRODUCT[item]}

    return {
        'status': 'success',
        'result': {
            'finished': finished_node,
            'unfinished': return_unfinished_node,
        },
    }

''' 日志配置 '''
def _logging_conf():
    try:
        global path_plan_logger
        logging.config.fileConfig('./conf/logging.conf')
        path_plan_logger = logging.getLogger('general')
        path_plan_logger.info('--------logging configurating successed--------')
        print('logging :%s' % id(path_plan_logger))
    except Exception as e:
        print('--------logging configurating failed--------')

def init():
    #global path_plan_logger
    start_time = time.time()
    _logging_conf()
    path_plan_logger.info('[starting] ----------initializing----------')

    # 加载每个学习提升任务对应数据库里的Node节点的ID
    path_plan_logger.info('[starting] loading NODE ID into dict . . . ')
    for each in open('resource/plan/activity.csv', 'r', encoding='utf-8').readlines():
        each = each.strip('\r\n').rstrip(' ')
        if each[:1] != '#':
            if each.find(',') > 0:
                node_name = each.split('//')[0].split(',')[1]
                node_id = int(each.split('//')[0].split(',')[0])
                NODE_DICT[node_name] = node_id
    path_plan_logger.info('[successed] loading NODE ID into dict . . . ')

    # 加载每个档次院校个学习提升任务的目标值
    path_plan_logger.info('[starting] loading target scores of different levels institutes into dict . . . ')
    for each in open('resource/plan/target.csv', 'r', encoding='utf-8').readlines():
        each = each.strip('\r\n').rstrip(' ')
        # print each
        target_name = each.split(',')[0]
        target_level = int(each.split(',')[1])
        target_score = float(each.split(',')[2])
        if target_level in TARGET_DICT:
            TARGET_DICT[target_level].update({target_name: target_score})
        else:
            TARGET_DICT.update({target_level: {target_name: target_score}})
    path_plan_logger.info('[successed] loading target scores of different levels institutes into dict . . . ')

    # 加载各个专业的每个学期的学习提升任务的安排
    path_plan_logger.info('[starting] loading weight of all parts in different semester into dict . . . ')
    path_plan_dirs = os.walk('resource/plan/weight')
    for root, dirs, files in path_plan_dirs:
        for temp_file in files:
            plan_path = os.path.join(root, temp_file)
            major = temp_file[0:temp_file.rfind('.')]
            temp_major_dict = {}
            for each in open(plan_path, 'r', encoding='utf-8').readlines():
                each = each.strip('\r\n').rstrip(' ')
                if each[:1] == '#':
                    semester = int(each[1])
                else:
                    if semester in temp_major_dict:
                        temp_major_dict[semester].update({each.split(',')[0]: float(each.split(',')[1])})
                    else:
                        temp_major_dict.update({semester: {each.split(',')[0]: float(each.split(',')[1])}})
            PATH_PLAN_DICT[major] = temp_major_dict
    path_plan_logger.info('[successed] loading weight of all parts in different semester into dict . . . ')

    # 从mongodb库里的product集合加载product信息
    path_plan_logger.info('[starting] loading product information from mongodb . . . ')
    try:
        for each in open('conf/db.conf', 'r', encoding='utf-8').readlines():
            try:
                each = each.strip('\r').strip('\n')
                if(each.split('=')[0] == 'mongodb.url'):
                    url = each.split('=')[1]
                if(each.split('=')[0] == 'mongodb.port'):
                    port = int(each.split('=')[1])
                if(each.split('=')[0] == 'mongodb.dulishuo.username'):
                    username = each.split('=')[1]
                if(each.split('=')[0] == 'mongodb.dulishuo.password'):
                    password = each.split('=')[1]
            except Exception as e:
                path_plan_logger.error(e)
                path_plan_logger.error('some line is wrong when read .')
                path_plan_logger.info('wrong line : %s ', each)
                return
    except FileNotFoundError:
        path_plan_logger.error('File resource/db.conf not found . . . ')
        return exit_error_func(3)
    except Exception as e:
        path_plan_logger.error(e)
        path_plan_logger.error('configuration failed.')

    mongo_client = MongoDB(host=url, port=port, username=username, password=password)
    product_collection = mongo_client.get_collection('product', 'dulishuo')
    for each in product_collection.find():
        try:
            if 'nodeParent' in each:
                node_parent = convert_to_int(each['nodeParent'])
                product_id = convert_to_int(each['id'])
                product_title = each['title']
                if 'title_pic' in each:
                    product_picture = each['title_pic']
                else:
                    product_picture = ''
                temp_product = {
                    'product_id': product_id,
                    'title': product_title,
                    'picture': product_picture
                }
                if node_parent == False:
                    continue
                if node_parent in NODE_PRODUCT:
                    temp_product_list = NODE_PRODUCT[node_parent]
                    temp_product_list.append(temp_product)
                    NODE_PRODUCT.update({node_parent: temp_product_list})
                else:
                    temp_product_list = [temp_product]
                    NODE_PRODUCT[node_parent] = temp_product_list
        except TypeError as e:
            path_plan_logger.error(e)
            path_plan_logger.error('wrong record when converting')
        except Exception as e:
            path_plan_logger.error(e)
            path_plan_logger.error('wrong record when converting')

    product_load_time = time.time()
    path_plan_logger.info('[successed] ending reading data from mongodb，use time %f s.' % (product_load_time - start_time))
    try:
        mongo_client.close() # 关闭连接
        path_plan_logger.info('close pymongo connection successed.')
    except Exception as e:
        path_plan_logger.error('close pymongo connection failed.')

    path_plan_logger.info('[successed] ----------initializing----------')
