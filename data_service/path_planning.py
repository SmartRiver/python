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
FIXED_NODES = [ #固定的结点（写文书、选择申请学校、网申、申请后工作）
    {
        'node_id': 79,
        'node_name': '写文书任务',
        'products': []
    },
    {
        'node_id': 80,
        'node_name': '选择申请学校列表',
        'products': []
    },
    {
        'node_id': 81,
        'node_name': '网上申请',
        'products': []
    },
    {
        'node_id': 94,
        'node_name': '申请后工作',
        'products': []
    }
] 
path_plan_logger = None # 日志
PATH_PLAN_DICT = {} # 各个专业每个学期的各学习提升任务权重值
TARGET_DICT = {} # 各个档次学校的每个部分的目标值
NODE_NAME_DICT = {} # 各个学习提升任务对应数据库里NODE表的ID
NODE_TYPE_DICT = {} # 各个NODE表ID对应各个学习提升任务的名字
NODE_TITLE_DICT = {} # 各个NODE表ID对应的前端卡片展示的title
NODE_DISPLAY_DICT = {} #各个学习提示功能任务对应前端展示的卡片名
NODE_PRODUCT = {} # product所属的NODE（大结点）
PRODUCT_RECOMMEND = {} # 每个Tag对应的推荐的机会产品
NODEID_TO_TEXT = {1:'提升GPA',3:'提升托福成绩',4:'提升雅思成绩',2:'提升GRE成绩',103:'提升GMAT成绩',11:'竞赛',6:'实习',12:'证书',102:'奖学金',14:'活动',104:'推荐信',5:'丰富科研经历'}

'''获取当前时间段(学期)'''
def _get_start_term(grade=1):
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

def _get_school_target(target):
    target = convert_to_int(target)
    if target in TARGET_LEVEL_LIST:
        return target
    elif target == False:
        return 4
    elif target not in TARGET_LEVEL_LIST:
        raise Exception('字段target不在[1-4]之间')

# 调用评估算法， 转化用户的信息
def _get_user_condition(user_input):
    return_assess_student = assess_student.assess(user_input)
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
def _get_language_exam_type(user_condition):
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

def _get_mgt(student_info):
    major = ''
    real_major = ''
    
    if 'major' in student_info:
        real_major = student_info['major']
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

    grade = _get_start_term(grade) # 将用户的年级（大一到大四[1-4]）按当前月份分为1-8
    target = _get_school_target(target) # 获取用户的目标院校档次
        
    return {
        'grade': grade,
        'target': target,
        'major': major,
        'real_major': real_major
    }

def _get_soft_condition(user_condition):
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

def _get_hard_condition(student_info, language_type, exam_type):
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
        elif language_type == 'toefl':
            temp_hard_condition['toefl'] = convert_to_float(user_data[language_type]['total'])
        else:
            temp_hard_condition['ielts'] = convert_to_float(user_data[language_type]['total'])
            temp_hard_condition['toefl'] = convert_to_float(user_data[language_type]['total'])
        if exam_type == 'gre':
            temp_hard_condition['gre'] = convert_to_float(user_data[exam_type]['total'])
        elif exam_type == 'gmat':
            temp_hard_condition['gmat'] = convert_to_float(user_data[exam_type]['total'])
        else:
            temp_hard_condition['gre'] = convert_to_float(user_data[exam_type]['total'])
            temp_hard_condition['gmat'] = convert_to_float(user_data[exam_type]['total'])
    except Exception as e:
        path_plan_logger.error('硬性条件比例获取时出错：'+str(e))
        return exit_error_func(6, '硬性条件比例获取时出错：'+str(e))

    return temp_hard_condition

def _filter_weight_field(weight_dict, language_type, exam_type):
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

def _calculate_nodes_weight(part_score_dict, language_type, exam_type):
    # 获取不同专业不同学期的初始化的各任务（节点）权重
    weight_dict = copy.deepcopy(PATH_PLAN_DICT[part_score_dict['major']][part_score_dict['grade']])
    #如果用户是toefl为主，则过滤ielts, 如果用户是gre,则过滤掉gmat, 反之过滤掉相反的，如果用户都没有，则全部保留
    _filter_weight_field(weight_dict, language_type, exam_type)

    target_dict = TARGET_DICT[part_score_dict['target']]

    unfinished_nodes = [] # 未完成的任务结点(存储的是结点ID)
    finished_nodes = [] # 已完成的任务结点(存储的是结点的内容such gpa)

    for each in weight_dict:
        if each in part_score_dict:
            if part_score_dict[each] >= target_dict[each]:
                _temp_target_score = TARGET_DICT[part_score_dict['target']][each]
                finished_nodes.append({
                    'node_id': NODE_NAME_DICT[each], 
                    'node_task_name': NODE_DISPLAY_DICT[NODE_NAME_DICT[each]], 
                    'node_title': NODE_TITLE_DICT[NODE_NAME_DICT[each]].replace('?', str(_temp_target_score)), 
                    'node_target': _temp_target_score,
                    })
            else:
                ratio = (target_dict[each] - part_score_dict[each]) / target_dict[each]
                weight_dict[each] = weight_dict[each] * (1+ratio)
                unfinished_nodes.append(each)
    result_weight = sorted(weight_dict.items(), key=lambda x:x[1], reverse=True)

    return finished_nodes, unfinished_nodes, result_weight

def _get_product_by_node_id(node_id, major, size=10):
    product_recommend = []
    if node_id in PRODUCT_RECOMMEND and major in PRODUCT_RECOMMEND:
        for product_by_attribute in PRODUCT_RECOMMEND[node_id]:
            for product_by_major in PRODUCT_RECOMMEND[major]:
                if product_by_attribute['title'] == product_by_major['title']:
                    product_recommend.append(product_by_attribute)
    else:
        return []
    _temp_prodict_size = len(product_recommend)
    if size == None:
        size = 10 if _temp_prodict_size > 10 else _temp_prodict_size
    if size > _temp_prodict_size:
        return product_recommend
    else:
        return product_recommend[:size]

def _get_reason_by_nodeid(semester, node_list, deviation_dict):
    #结果字典
    result_dict = {}
    #学期（数字）转学期（中文）字典
    semester_dict = {1:'大一上学期', 2:'大一下学期', 3:'大二上学期', 4:'大二下学期', 5:'大三上学期', 6:'大三下学期'}
    #学期（数字）转年级（中文）字典
    grade_dict = {1:'大一', 2:'大一', 3:'大二', 4:'大二', 5:'大三', 6:'大三'}
    for attribute in deviation_dict:
        if attribute in REASON_DICT['special']:
            deviation = deviation_dict[attribute]
            for row in REASON_DICT['special'][attribute]:
                if deviation >= float(row[0].split('-')[0]) and deviation < float(row[0].split('-')[1]) and row[1].count(str(semester)) > 0:
                    result_dict[NODE_NAME_DICT[attribute]]= {}
                    result_dict[NODE_NAME_DICT[attribute]]['what'] = row[2].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
                    result_dict[NODE_NAME_DICT[attribute]]['how'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
             
    #反转节点字典
    node_name_dict = dict((v,k) for k, v in NODE_NAME_DICT.items())

    #两项对比
    compare = list(map(lambda x:node_name_dict[x['nodeid']], node_list[:3]))
    
    if len(compare) >=2:
        success = 0
        #在前三项的第一项和第二项产生比较，必然第一项>第二项
        for row in REASON_DICT['compare']:
            if row[0] == compare[0]:
                if row[1] == compare[1]:
                    if row[2].count(str(semester)) > 0:
                        result_dict[NODE_NAME_DICT[compare[0]]] = {'what':row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
                        result_dict[NODE_NAME_DICT[compare[1]]] = {'what':row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
                        success = 1
        
        if not success == 1 and len(compare) >= 3:
            #第一项和第三项产生比较，必然第一项>第三项
            for row in REASON_DICT['compare']:
                if row[0] == compare[0]:
                    if row[1] == compare[2]:
                        if row[2].count(str(semester)) > 0:
                            result_dict[NODE_NAME_DICT[compare[0]]] = {'what':row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
                            result_dict[NODE_NAME_DICT[compare[2]]] = {'what':row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
                            success = 1
                        
        if not success == 1 and len(compare) >= 3:
            #第二项和第三项产生比较，必然第二项>第三项
            for row in REASON_DICT['compare']:
                if row[0] == compare[1]:
                    if row[1] == compare[2]:
                        if row[2].count(str(semester)) > 0:
                            result_dict[NODE_NAME_DICT[compare[1]]] = {'what':row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
                            result_dict[NODE_NAME_DICT[compare[2]]] = {'what':row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]),'how':row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])}
    #优先级高
    for node in node_list[:3]:
        if node['nodeid'] in result_dict:
            continue
        result_dict[node['nodeid']] = {}
        result_dict[node['nodeid']]['what'] = REASON_DICT['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
        result_dict[node['nodeid']]['how'] = REASON_DICT['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
    #优先级低
    for node in node_list[3:]:
        if node['nodeid'] in result_dict:
            continue
        result_dict[node['nodeid']] = {}
        result_dict[node['nodeid']]['what'] = REASON_DICT['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
        result_dict[node['nodeid']]['how'] = REASON_DICT['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester])
    return result_dict

def _get_nodes_products(part_score_dict, language_type, exam_type, size):
    unfinished_nodes_products = [] # 未完成任务结点（关联了相应的机会产品、项目）
    return_unfinished_nodes = [] # 未完成任务结点（存储的是结点ID）

    # 计算各个结点的权值，按照计算后的权重值对各个学习提升任务排序
    finished_nodes, unfinished_nodes, result_weight = _calculate_nodes_weight(part_score_dict, language_type, exam_type)
    path_plan_logger.info('calculate_nodes_weight')

    for each in result_weight:
        if each[0] in unfinished_nodes:
            return_unfinished_nodes.append(NODE_NAME_DICT[each[0]])
    deviation_list = list(map(lambda x:round(TARGET_DICT[part_score_dict['target']][x] - part_score_dict[x],2),['gpa', exam_type, language_type]))
    deviation_dict = {'gpa':deviation_list[0], exam_type:deviation_list[1], language_type:deviation_list[2]}
    _temp_unfinished_nodes = list(map(lambda x:{'nodeid':x}, return_unfinished_nodes))
    for each in list(map(lambda x:{'nodeid': x['node_id']}, finished_nodes)):
        _temp_unfinished_nodes.append(each)
    #获取推荐理由
    reason_dict = _get_reason_by_nodeid(part_score_dict['grade'], _temp_unfinished_nodes, deviation_dict)
    for index,item in enumerate(return_unfinished_nodes):
        _temp_target_score = TARGET_DICT[part_score_dict['target']][NODE_TYPE_DICT[item]]
        if NODEID_TO_TEXT[item] in PRODUCT_RECOMMEND:
            unfinished_nodes_products.append({
                'node_id': item,
                'node_task_name': NODE_DISPLAY_DICT[item],
                'node_title': NODE_TITLE_DICT[item].replace('?', str(_temp_target_score)),
                'node_target': _temp_target_score,
                'what': reason_dict[item]['what'],
                'how':reason_dict[item]['how'],
                'products': _get_product_by_node_id(NODEID_TO_TEXT[item], part_score_dict['real_major'], size),
                })
        else:
            unfinished_nodes_products.append({
                'node_id': item,
                'node_task_name': NODE_DISPLAY_DICT[item],
                'node_title': NODE_TITLE_DICT[item].replace('?', str(_temp_target_score)),
                'node_target': _temp_target_score,
                'what': reason_dict[item]['what'],
                'how':reason_dict[item]['how'],
                'products': [],
                })
    #为硬实力做特殊处理
    for index, item in enumerate(unfinished_nodes_products):
        unfinished_nodes_products[index]['field'] = NODE_TYPE_DICT[item['node_id']]
        if item['node_id'] in [1, 2, 3, 4, 103]:
            unfinished_nodes_products[index]['node_name'] = item['node_task_name'].replace('任务', '')
            unfinished_nodes_products[index]['node_score'] = part_score_dict[NODE_TYPE_DICT[item['node_id']]]
        else:
            unfinished_nodes_products[index]['node_target'] = ''
            unfinished_nodes_products[index]['node_score'] = ''

    for index, item in enumerate(finished_nodes):
        finished_nodes[index]['what'] = reason_dict[item['node_id']]['what']
        finished_nodes[index]['how'] = reason_dict[item['node_id']]['how']
        finished_nodes[index]['field'] = NODE_TYPE_DICT[item['node_id']]
        if item['node_id'] in [1, 2, 3, 4, 103]:
            finished_nodes[index]['node_name'] = item['node_task_name'].replace('任务', '')
            finished_nodes[index]['node_score'] = part_score_dict[NODE_TYPE_DICT[item['node_id']]]
        else:
            finished_nodes[index]['node_target'] = ''
            finished_nodes[index]['node_score'] = ''      
    #unfinished_nodes_products.extend(FIXED_NODES)

    return finished_nodes, unfinished_nodes_products

def _get_return_target(target, language_type, exam_type):
    return_target_dict = {}
    target = TARGET_DICT[target]
    return_target_dict['gpa'] = {'type': 'GPA', 'score': target['gpa']}
    if language_type in ['toefl', 'ielts']:
        return_target_dict['language'] = {'type': language_type.upper() , 'score': target[language_type]}
    else:
        return_target_dict['language'] = {'type': 'TOEFL/IELTS', 'score': target['toefl']+'/'+target['ielts']}
    if exam_type in ['gre', 'gmat']:
        return_target_dict['exam'] = {'type': exam_type.upper(), 'score': target[exam_type]}
    else:
        return_target_dict['exam'] = {'type': 'GRE/GMAT', 'score': target['gre']+'/'+target['gmat']}

    return return_target_dict

def _check_schedule_size(size):
    if size == None:
        return size
    size = convert_to_int(size)
    if size < 1:
        raise ValueError('size应为大于0的整数')
    else:
        return size

def schedule(condition, size=None):
    part_score_dict = {}
    try:
        #size 校对是否为大于0的整数
        size = _check_schedule_size(size)

        # 调用assess_student模块的assess(), 提取出所需要的用户信息
        user_condition = _get_user_condition(condition) 

        # 确定用户的语言类型（toefl or ielts）、（gre or gmat)
        language_type, exam_type = _get_language_exam_type(user_condition)

        #确定'student_info'字段是否存在
        if 'student_info' in user_condition:
            student_info = user_condition['student_info']
        else:
            path_plan_logger.error('缺少字段student_info')
            raise Exception('缺少字段student_info')

        #提取出用户的申请属性（major、 grade、 target）
        part_score_dict.update(_get_mgt(student_info))
        path_plan_logger.info('[successed] _get_mgt()')

        # 提取出用户的硬性指标（gpa、 toefl/ielts、 gre/gmat）
        part_score_dict.update(_get_hard_condition(student_info, language_type, exam_type))
        path_plan_logger.info('[successed] _get_hard_condition()')

        #提取用户的软性指标（activity、 scholarship、 internship、 research、 credential、 competition）
        part_score_dict.update(_get_soft_condition(user_condition))
        path_plan_logger.info('[successed] _get_soft_condition()')

        # 为学习提升任务结点关联相应的机会产品
        finished_nodes, unfinished_nodes_products = _get_nodes_products(part_score_dict, language_type, exam_type, size)

        path_plan_logger.info('[successed] _get_nodes_products()')

        return_target = _get_return_target(part_score_dict['target'], language_type, exam_type)
        path_plan_logger.info('[successed] _get_return_target()')
        
    except Exception as e:
        return exit_error_func(1, '接口调用失败，错误信息：'+str(e)+', 异常类型：'+str(type(e)))

    
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
            'user_condition': user_condition,
            'target': return_target,
            'finished': finished_nodes,
            'unfinished': unfinished_nodes_products,
        },
    }

def _logging_conf():
    ''' 日志配置 '''
    try:
        global path_plan_logger
        logging.config.fileConfig('./conf/logging.conf')
        path_plan_logger = logging.getLogger('general')
        path_plan_logger.info('--------logging configurating successed--------')
    except Exception as e:
        print('--------logging configurating failed--------')

def _load_node():
    path_plan_logger.info('[starting] loading NODE ID into dict . . . ')
    
    for each in open('resource/plan/activity.csv', 'r', encoding='utf-8').readlines():
        each = each.strip('\r\n').rstrip(' ')
        if each[:1] != '#':            
            if each.find(',') > 0:
                each = each.split('//')[0]
                node_id = int(each.split(',')[0]) # 结点ID
                node_name = each.split(',')[1] # 结点Node名字
                node_display_name = each.split(',')[2] # 前端展示的任务卡的名字
                node_title = each.split(',')[3] # 前端展示的任务卡的标题
                NODE_NAME_DICT[node_name] = node_id
                NODE_TYPE_DICT[node_id] = node_name
                NODE_DISPLAY_DICT[node_id] = node_display_name
                NODE_TITLE_DICT[node_id] = node_title
    path_plan_logger.info('[successed] loading NODE ID into dict . . . ')

def _load_target():
    path_plan_logger.info('[starting] loading target scores of different levels institutes into dict . . . ')
    for each in open('resource/plan/target.csv', 'r', encoding='utf-8').readlines():
        each = each.strip('\r\n').rstrip(' ')
        # print each
        target_name = each.split(',')[0]
        target_level = int(each.split(',')[1])
        target_score = float(each.split(',')[2])
        if each.split(',')[2].find('.') > 0:
            target_score = float(each.split(',')[2])
        else:
            target_score = int(each.split(',')[2])
        if target_level in TARGET_DICT:
            TARGET_DICT[target_level].update({target_name: target_score})
        else:
            TARGET_DICT.update({target_level: {target_name: target_score}})
    path_plan_logger.info('[successed] loading target scores of different levels institutes into dict . . . ')

def _load_init_weight():
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

def _get_tag_dict(tag_list, collection):
    for major in assess_student.MAJOR:
        tag_list.append(major)
    tag_dict = {}
    for tag_name in tag_list:
        result = collection.find_one({'name':tag_name},{'id':1})
        if isinstance(result, dict):
            tag_dict[tag_name] = '%d'%result['id']
    return tag_dict

def _load_products_by_tag():
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
    path_plan_logger.info('[successed] load resource/db.conf')
    mongo_client = MongoDB(host=url, port=port, username=username, password=password, auth=True)
    mongo_client.get_database('dulishuo')
    product_collection = mongo_client.get_collection('product')
    producttag_collection = mongo_client.get_collection('producttag')
    tag_list = ['提升GPA','提升托福成绩','提升雅思成绩','提升GRE成绩','提升GMAT成绩','竞赛','实习','证书','奖学金','活动','推荐信','科研能力提升']
    tag_dict = _get_tag_dict(tag_list,producttag_collection)
    path_plan_logger.info('[successed] get tag dict')
    
    for tag_name in tag_dict:
        producs_list = []
        for record in product_collection.find({'tag':{'$regex':tag_dict[tag_name]}},{'id':1,'title':1,'title_pic':1,'tag':1}):
            product = {}
            try:
                product['product_id'] = record['id']
                product['title'] = record['title']
                product['picture'] = record['title_pic']
            except KeyError:
                continue
            producs_list.append(product)
        PRODUCT_RECOMMEND[tag_name] = producs_list
    product_load_time = time.time()
    try:
        mongo_client.close() # 关闭连接
        path_plan_logger.info('close pymongo connection successed.')
    except Exception as e:
        path_plan_logger.error('close pymongo connection failed.')

def _load_reason():
    path_plan_logger.info('[starting] loading reason of different nodes from reason.csv to dict.')
    global REASON_DICT
    REASON_DICT = {}
    file = open('resource'+os.sep+'reason'+os.sep+'reason.csv', 'r', encoding='utf-8')
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        line = list(map(lambda column: column.strip('\n').strip(), line.split('|')))
        if line[0] == 'common':
            if line[0] in REASON_DICT:
                if line[1] in REASON_DICT[line[0]]:
                    REASON_DICT[line[0]][line[1]][line[2]] = line[3]+'|'+line[4]
                else:
                    REASON_DICT[line[0]][line[1]] = {}
                    REASON_DICT[line[0]][line[1]][line[2]] = line[3]+'|'+line[4]
            else:
                REASON_DICT[line[0]] = {}
                REASON_DICT[line[0]][line[1]] = {}
                REASON_DICT[line[0]][line[1]][line[2]] = line[3]+'|'+line[4]
        elif line[0] == 'special':
            if line[0] in REASON_DICT:
                if line[1] in REASON_DICT[line[0]]:
                    REASON_DICT[line[0]][line[1]].append(line[2:])
                else:
                    REASON_DICT[line[0]][line[1]] = []
                    REASON_DICT[line[0]][line[1]].append(line[2:])
            else:
                REASON_DICT[line[0]] = {}
                REASON_DICT[line[0]][line[1]] = []
                REASON_DICT[line[0]][line[1]].append(line[2:])
        elif line[0] == 'compare':
            if line[0] in REASON_DICT:
                REASON_DICT[line[0]].append(line[1:])
            else:
                REASON_DICT[line[0]] = []
                REASON_DICT[line[0]].append(line[1:])
                
    path_plan_logger.info('[successed] loading reason of different nodes from reason.csv to dict.')

def init():
    start_time = time.time()

    _logging_conf() #初始化日志设置

    path_plan_logger.info('[starting] ----------initializing----------')

    _load_node() # 加载每个学习提升任务对应数据库里的Node节点的ID

    _load_target() # 加载每个档次院校个学习提升任务的目标值
    
    _load_init_weight() # 加载各个专业的每个学期的学习提升任务的安排(按照咨询师给的初始权重值排序)
    
    _load_products_by_tag() # 从mongodb库里的product集合加载product信息,并按标签tag分类

    _load_reason() # 从配置文件[reason/reason.csv]中加载文案
    
    path_plan_logger.info('[successed] ----------initializing----------')
