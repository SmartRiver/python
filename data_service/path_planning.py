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
FIXED_NODES = [79,80,81,94] #固定的结点（写文书、选择申请学校、网申、申请后工作）
path_plan_logger = None # 日志
PATH_PLAN_DICT = {} # 各个专业每个学期的各学习提升任务权重值
TARGET_DICT = {} # 各个档次学校的每个部分的目标值
NODE_DICT = {} # 各个学习提升任务对应数据库里NODE表的ID
NODE_PRODUCT = {} #product所属的NODE（大结点）

'''获取当前时间段(学期)'''
def get_start_term(grade=1):
    grade = convert_to_int(grade)
    if grade == False or grade not in GRADE_LEVEL_LSIT:
        raise Exception('字段grade不在[1-4]之间')
    now_month = time.localtime().tm_mon # 获取当前的月份
    if 3 <= now_month <= 8:
        increase = 0
    else:
        increase = -1
    grade = grade * 2 + increase
    return grade

def get_target(target):
    target = convert_to_int(target)
    if target in TARGET_LEVEL_LIST:
        return target
    elif target == False:
        return 4
    elif target not in TARGET_LEVEL_LIST:
        raise Exception('字段target不在[1-4]之间')

# 调用评估算法， 转化用户的信息
def get_user_condition(user_input):
    return_assess_student = assess_student.assess(user_input)
    print(json.dumps(return_assess_student, ensure_ascii=False, indent=4))
    if 'result' in return_assess_student:
        return return_assess_student['result']
    else:
        if 'msg' in return_assess_student:
            path_plan_logger.error('调用assess_student模块的assess出错：'+return_assess_student['msg'])
            raise Exception(return_assess_student['msg'])
        else:
            path_plan_logger.error('调用assess_student模块的assess出错：'+return_assess_student)
            raise Exception(return_assess_student)
    
# 确定用户的语言类型（toefl or ielts）、（gre or gmat)
def get_language_exam_type(user_condition):
    if 'language_type' in user_condition:
        language_type = convert_to_str(user_condition['language_type'])
        if language_type not in ['ielts', 'toefl', 'neither', 'none']: # 用户的语言类型，neither表示两者都不
            path_plan_logger.error('无效的属性值language_type')
            raise Exception('无效的属性值language_type')
    else:
        path_plan_logger.error('缺少字段language_type')
        raise Exception('缺少字段language_type')

    if 'exam_type' in user_condition:
        exam_type = convert_to_str(user_condition['exam_type'])
        if exam_type not in ['gre', 'gmat', 'neither', 'none']:
            path_plan_logger.error('无效的属性值exam_type')
            raise Exception('无效的属性值exam_type')
    else:
        path_plan_logger.error('缺少字段exam_type')
        raise Exception('缺少字段exam_type')
    return language_type, exam_type

def get_mgt(student_info):
    if 'major' in student_info:
        major = student_info['major']
        major = convert_to_str(major)
        if major not in PATH_PLAN_DICT:
            major = 'general'
    else:
        path_plan_logger.error('缺失字段[student_info][major]')
        raise Exception('缺失字段[student_info][major]')
    if 'target' in student_info:
        target = student_info['target']
    else:
        path_plan_logger.error('缺失字段[student_info][target]')
        raise Exception('缺失字段[student_info][target]')
    if 'grade' in student_info:
        grade = student_info['grade']
    else:
        path_plan_logger.error('缺失字段[student_info][grade]')
        raise Exception('缺失字段[student_info][grade]')

    grade = get_start_term(grade) # 将用户的年级（大一到大四[1-4]）按当前月份分为1-8
    target = get_target(target) # 获取用户的目标院校档次
        
    return {
        'grade': grade,
        'target': target,
        'major': major
    }

def get_soft_condition(user_condition):
    if 'dimension' in user_condition:
        dimension = user_condition['dimension']
    else:
        path_plan_logger.error('缺少字段dimension')
        raise Exception('缺少字段dimension')

    if 'dimension_full' in user_condition:
        dimension_full = user_condition['dimension_full']
    else:
        path_plan_logger.error('缺少字段dimension_full')
        raise Exception('缺少字段dimension_full')
    temp_soft_condition = {}
    try:
        if 'research_dimension' in dimension:
            temp_soft_condition['research'] = convert_to_float(dimension['research_dimension'])/convert_to_float(dimension_full['research_dimension'])
        if 'internship_dimension' in dimension:
            temp_soft_condition['internship'] = convert_to_float(dimension['internship_dimension'])/convert_to_float(dimension_full['internship_dimension'])
        if 'activity_dimension' in dimension:
            temp_soft_condition['activity'] = convert_to_float(dimension['activity_dimension'])/convert_to_float(dimension_full['activity_dimension'])
        if 'scholarship_dimension':
            temp_soft_condition['scholarship'] = convert_to_float(dimension['scholarship_dimension'])/convert_to_float(dimension_full['scholarship_dimension'])
        if 'credential_dimension' in dimension:
            temp_soft_condition['credential'] = convert_to_float(dimension['credential_dimension'])/convert_to_float(dimension_full['credential_dimension'])
        if 'competition_dimension' in dimension:
            temp_soft_condition['competition'] = convert_to_float(dimension['competition_dimension'])/convert_to_float(dimension_full['competition_dimension'])
    except Exception as e:
        path_plan_logger.error('软性条件比例获取时出错：'+str(e))
        return exit_error_func(6, '软性条件比例获取时出错：'+str(e))

    return temp_soft_condition

def get_hard_condition(student_info, language_type, exam_type):
    if 'data' in student_info:
        user_data = student_info['data']
    else:
        path_plan_logger.error('缺少字段student_info[data]')
        raise Exception('缺少字段student_info[data]')
    temp_hard_condition = {}
    try:
        temp_hard_condition['gpa'] = convert_to_float(user_data['gpa']['score'])
        if language_type == 'ielts':
            temp_hard_condition['ielts'] = convert_to_float(user_data[language_type]['total'])
        if language_type == 'toefl':
            temp_hard_condition['toefl'] = convert_to_float(user_data[language_type]['total'])
        if exam_type == 'gre':
            temp_hard_condition['gre'] = convert_to_float(user_data[exam_type]['total'])
        if exam_type == 'gmat':
            temp_hard_condition['gmat'] = convert_to_float(user_data[exam_type]['total'])
    except Exception as e:
        path_plan_logger.error('硬性条件比例获取时出错：'+str(e))
        return exit_error_func(6, '硬性条件比例获取时出错：'+str(e))

    return temp_hard_condition

def filter_weight_field(weight_dict, language_type, exam_type):
    if language_type == 'ielts':
        if 'toefl' in weight_dict:
            del weight_dict['toefl']
    elif language_type == 'toefl':
        if 'ielts' in weight_dict:
            del weight_dict['ielts']
    elif language_type == 'none':
        if 'ielts' in weight_dict:
            del weight_dict['ielts']
        if 'toefl' in weight_dict:
            del weight_dict['toefl']
    if exam_type == 'gre':
        if 'gmat' in weight_dict:
            del weight_dict['gmat']
    elif exam_type == 'gmat':
        if 'gre' in weight_dict:
            del weight_dict['gre']
    elif exam_type == 'none':
        if 'gmat' in weight_dict:
            del weight_dict['gmat']
        if 'gre' in weight_dict:
            del weight_dict['gre']

def calculate_nodes_weight(part_score_dict, language_type, exam_type):
    # 获取不同专业不同学期的初始化的各任务（节点）权重
    weight_dict = copy.deepcopy(PATH_PLAN_DICT[part_score_dict['major']][part_score_dict['grade']])
    #如果用户是toefl为主，则过滤ielts, 如果用户是gre,则过滤掉gmat, 反之过滤掉相反的，如果用户都没有，则全部保留
    filter_weight_field(weight_dict, language_type, exam_type)

    target_dict = TARGET_DICT[part_score_dict['target']]

    unfinished_nodes = [] # 未完成的任务结点(存储的是结点ID)
    finished_nodes = [] # 已完成的任务结点(存储的是结点的内容such gpa)

    for each in weight_dict:
        if each in part_score_dict:
            if part_score_dict[each] > target_dict[each]:
                finished_nodes.append(NODE_DICT[each])
            else:
                ratio = (target_dict[each] - part_score_dict[each]) / target_dict[each]
                weight_dict[each] = weight_dict[each] * (1+ratio)
                unfinished_nodes.append(each)
    result_weight = sorted(weight_dict.items(), key=lambda x:x[1], reverse=True)

    return finished_nodes, unfinished_nodes, result_weight

def get_nodes_products(part_score_dict, language_type, exam_type):

    unfinished_nodes_products = [] # 未完成任务结点（关联了相应的机会产品、项目）
    return_unfinished_nodes = [] # 未完成任务结点（存储的是结点ID）

    # 计算各个结点的权值，按照计算后的权重值对各个学习提升任务排序
    finished_nodes, unfinished_nodes, result_weight = calculate_nodes_weight(part_score_dict, language_type, exam_type)

    for each in result_weight:
        if each[0] in unfinished_nodes:
            return_unfinished_nodes.append(NODE_DICT[each[0]])
    return_unfinished_nodes.extend(FIXED_NODES)

    for index,item in enumerate(return_unfinished_nodes):
        if item in NODE_PRODUCT:
            unfinished_nodes_products.append({'node_id': item, 'products': NODE_PRODUCT[item]})
        else:
            unfinished_nodes_products.append({'node_id': item, 'products': []})
    return finished_nodes, unfinished_nodes_products
    
def schedule(user_input):
    part_score_dict = {}
    try:
        # 调用assess_student模块的assess(), 提取出所需要的用户信息
        user_condition = get_user_condition(user_input) 

        # 确定用户的语言类型（toefl or ielts）、（gre or gmat)
        language_type, exam_type = get_language_exam_type(user_condition)

        #确定'student_info'字段是否存在
        if 'student_info' in user_condition:
            student_info = user_condition['student_info']
        else:
            path_plan_logger.error('缺少字段student_info')
            raise Exception('缺少字段student_info')

        #提取出用户的申请属性（major、 grade、 target）
        part_score_dict.update(get_mgt(student_info))

        # 提取出用户的硬性指标（gpa、 toefl/ielts、 gre/gmat）
        part_score_dict.update(get_hard_condition(student_info, language_type, exam_type))

        #提取用户的软性指标（activity、 scholarship、 internship、 research、 credential、 competition）
        part_score_dict.update(get_soft_condition(user_condition))

        # 为学习提升任务结点关联相应的机会产品
        finished_nodes, unfinished_nodes_products = get_nodes_products(part_score_dict, language_type, exam_type)
        
    except Exception as e:
        return exit_error_func(1, '接口调用失败，错误信息：'+str(e))

    
    #for index,item in enumerate(finished_node):
    #    finished_node[index] = {'node_id': item, 'products': []}
    #    if item in NODE_PRODUCT:
    #        finished_node[index] = {'node_id': item, 'products': NODE_PRODUCT[item]}
    
    # for index,item in enumerate(return_node):
    #     return_node[index] = {item: []}
    #     if item in NODE_PRODUCT:
    #         return_node[index] = {item: NODE_PRODUCT[item]}

    return {
        'status': 'success',
        'result': {
            'finished': finished_nodes,
            'unfinished': unfinished_nodes_products,
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

def load_node():
    path_plan_logger.info('[starting] loading NODE ID into dict . . . ')
    for each in open('resource/plan/activity.csv', 'r', encoding='utf-8').readlines():
        each = each.strip('\r\n').rstrip(' ')
        if each[:1] != '#':
            if each.find(',') > 0:
                node_name = each.split('//')[0].split(',')[1]
                node_id = int(each.split('//')[0].split(',')[0])
                NODE_DICT[node_name] = node_id
    path_plan_logger.info('[successed] loading NODE ID into dict . . . ')

def load_target():
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

def load_init_weight():
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

def load_products():
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
        path_plan_logger.error(3, 'mongodb configuration failed.')
        return exit_error_func(3)

    mongo_client = MongoDB(host=url, port=port, username=username, password=password, auth=True)
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
    path_plan_logger.info('[successed] ending reading data from mongodb.')
    try:
        mongo_client.close() # 关闭连接
        path_plan_logger.info('close pymongo connection successed.')
    except Exception as e:
        path_plan_logger.error('close pymongo connection failed.')

def init():

    start_time = time.time()

    _logging_conf() #初始化日志设置

    path_plan_logger.info('[starting] ----------initializing----------')

    load_node() # 加载每个学习提升任务对应数据库里的Node节点的ID

    load_target()# 加载每个档次院校个学习提升任务的目标值
    
    load_init_weight()# 加载各个专业的每个学期的学习提升任务的安排(按照咨询师给的初始权重值排序)
    
    load_products()# 从mongodb库里的product集合加载product信息
    
    path_plan_logger.info('[successed] ----------initializing----------')
