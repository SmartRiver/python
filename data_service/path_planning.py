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
GRADE_LEVEL_LSIT = [1, 2, 3] # 年级 1、2、3、4分半代表大一、大二、大三、大四
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
USER_ANALYSIS = {} # 咨询师为不同用户设置的软、硬件分析文案
ANALYSIS_TABLE = [
                ('gpa', 'gpa_score', 1, 0, 0, 'GPA'),
                ('school', 'gpa_school', 1, 1, 12, '学校'),
                ('toefl', 'toefl_total', 1, 0, 0, '托福'),
                ('toefl_speaking', 'toefl_speaking', 1, 0, 0),
                ('ielts', 'ielts_total', 1, 0, 0, '雅思'),
                ('ielts_speaking', 'ielts_speaking', 1, 0, 0),
                ('gre', 'gre_total', 1, 0, 0, 'GRE'),
                ('gre_writing', 'gre_writing', 1, 0, 0),
                ('gmat', 'gmat_total', 1, 0, 0, 'GMAT'),
                ('gmat_writing', 'gmat_writing', 1, 0, 0),
                ('research_duration', 'research_duration', 0, 1, 4, '科研能力'),
                ('research_level', 'research_level', 0, 1, 4),
                ('research_achievement', 'research_achievement', 0, 1, 4),
                ('internship_duration', 'internship_duration', 0, 1, 4, '实习'),
                ('internship_level', 'internship_level', 0, 1, 3),
                ('internship_recommendation', 'internship_recommendation', 0, 1, 3),
                ('competition', 'competition_level', 0, 1, 5, '竞赛获奖'),
                ('activity_duration', 'activity_duration', 0, 1, 3, '活动经历'),
                ('activity_level', 'activity_type', 0, 1, 4)
                ]
NODEID_TO_TEXT = {1:'提升GPA',3:'提升托福成绩',4:'提升雅思成绩',2:'提升GRE成绩',103:'提升GMAT成绩',11:'竞赛',6:'实习',12:'证书',102:'奖学金',14:'活动',104:'推荐信',5:'科研能力提升'}

'''获取当前时间段(学期)'''
def _get_start_term(grade=1):
    grade = convert_to_int(grade)
    if grade == False or grade not in GRADE_LEVEL_LSIT:
        raise Exception('字段grade不在[1-3]之间')
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
        dimension_dict = user_condition['dimension']
    else:
        path_plan_logger.error('缺少字段dimension')
        raise Exception('缺少字段dimension')

    if 'dimension_full' in user_condition:
        dimension_full_dict = user_condition['dimension_full']
    else:
        path_plan_logger.error('缺少字段dimension_full')
        raise Exception('缺少字段dimension_full')
    temp_soft_condition = {}
    try:
        for dimension in dimension_dict:
            if not dimension.split('_')[0] == 'gpa' and not dimension.split('_')[0] == 'exam' and not dimension.split('_')[0] == 'language':
                temp_soft_condition[dimension.split('_')[0]] = convert_to_float(dimension_dict[dimension])/convert_to_float(dimension_full_dict[dimension])
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
    #user_data 为筛选过后的学生输入
    temp_hard_condition = {}
    try:
        temp_hard_condition['gpa'] = convert_to_float(user_data['gpa']['score'])
        
        if language_type == 'ielts':
            temp_hard_condition['ielts'] = convert_to_float(user_data[language_type]['total'])
        elif language_type == 'toefl':
            temp_hard_condition['toefl'] = convert_to_float(user_data[language_type]['total'])
        elif language_type == 'neither':
            temp_hard_condition['ielts'] = 0
            temp_hard_condition['toefl'] = 0
        else:
            pass
            
        if exam_type == 'gre':
            temp_hard_condition['gre'] = convert_to_float(user_data[exam_type]['total'])
        elif exam_type == 'gmat':
            temp_hard_condition['gmat'] = convert_to_float(user_data[exam_type]['total'])
        elif exam_type == 'neither':
            temp_hard_condition['gre'] = 0
            temp_hard_condition['gmat'] = 0
        else:
            pass
  
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
    else:
        pass#都保留
        
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
    else:
        pass#都保留

def _calculate_nodes_weight(part_score_dict, language_type, exam_type):

    # 获取不同专业不同学期的初始化的各任务（节点）权重
    if part_score_dict['major'] in assess_student.MAJOR:
        weight_dict = copy.deepcopy(PATH_PLAN_DICT[assess_student.MAJOR[part_score_dict['major']]][part_score_dict['grade']])
    else:
        weight_dict = copy.deepcopy(PATH_PLAN_DICT[part_score_dict['major']][part_score_dict['grade']])
    
    #如果用户是toefl为主，则过滤ielts, 如果用户是gre,则过滤掉gmat, 反之过滤掉相反的，如果用户都没有，则全部保留
    _filter_weight_field(weight_dict, language_type, exam_type)
    
    target_dict = TARGET_DICT[part_score_dict['target']]
    unfinished_nodes = [] # 未完成的任务结点(存储的是结点ID)
    finished_nodes = [] # 已完成的任务结点(存储的是结点的内容such gpa)
    #对于每一个权值的键
    for each in weight_dict:
        #如果该键在part_score_dict出现
        if each in part_score_dict:
            #如果part_score_dict中的该键的值大于等于目标中该键的值(属性的值)
            if part_score_dict[each] >= target_dict[each]:
                _temp_target_score = TARGET_DICT[part_score_dict['target']][each]
                #则向已完成节点中追加完成节点的信息（无序）
                if not each == 'activity':
                    finished_nodes.append({
                        'node_id': NODE_NAME_DICT[each], 
                        'node_task_name': NODE_DISPLAY_DICT[NODE_NAME_DICT[each]], 
                        'node_title': NODE_TITLE_DICT[NODE_NAME_DICT[each]].replace('?', str(_temp_target_score)), 
                        'node_target': _temp_target_score,
                        })
            #如果part_score_dict中的改键的值小于目标中该键的值（属性的值）
            else:
                #求出当前值与目标值之间相差的比例，并和weight_dict中对应的权值相乘，替换原有的项
                ratio = (target_dict[each] - part_score_dict[each]) / target_dict[each]
                if each == 'gpa':
                    if ratio < 0.5:
                        ratio = ratio + 0.25
                elif each in ['toefl', 'ielts', 'gre', 'gmat']:
                    if ratio > 0.9:
                        ratio = 0.3
                    elif ratio < 0.5:
                        ratio = ratio + 0.3
                else:
                    if ratio > 0.65:
                        ratio = 0.5
                    elif ratio > 0.5:
                        ratio = 0.45
                weight_dict[each] = weight_dict[each] * ratio
                unfinished_nodes.append(each)
    # for each in sorted(weight_dict.items(), key=lambda x:x[1], reverse=True):
    #     print(each[0]+'\t'+str(each[1]))
    #对结果进行排序
    result_weight = sorted(weight_dict.items(), key=lambda x:x[1], reverse=True)
    return finished_nodes, unfinished_nodes, result_weight

def _get_product_by_node_id(node_id, major, size=10):
    product_recommend = []
    major_only = major + '_only'
    if major in assess_student.MAJOR:
        major_type = assess_student.MAJOR[major]
    else:
        return []

    #先找结点相关，专业only
    #如果存在该结点相关和专业only
    if node_id in PRODUCT_RECOMMEND and major_only in PRODUCT_RECOMMEND:
        for product_by_attribute in PRODUCT_RECOMMEND[node_id]:
            for product_by_major_only in PRODUCT_RECOMMEND[major_only]:
                if product_by_attribute['title'] == product_by_major_only['title']:
                    product_recommend.append(product_by_attribute)
    

    #然后找结点相关，专业相关
    #如果存在该结点相关和专业
    if node_id in PRODUCT_RECOMMEND and major in PRODUCT_RECOMMEND:
        temp_product_recommend = []
        for product_by_attribute in PRODUCT_RECOMMEND[node_id]:
            for product_by_major in PRODUCT_RECOMMEND[major]:
                if product_by_attribute['title'] == product_by_major['title']:
                    temp_product_recommend.append(product_by_attribute)
    #合并列表，去除重复   
    for product in temp_product_recommend:
        if not product in product_recommend:
            product_recommend.append(product)

    #然后找结点相关，专业大类相关
    #如果存在该结点相关和专业大类                   
    if node_id in PRODUCT_RECOMMEND and major_type in PRODUCT_RECOMMEND:
        temp_product_recommend = []
        for product_by_attribute in PRODUCT_RECOMMEND[node_id]:
            for product_by_major_type in PRODUCT_RECOMMEND[major_type]:
                if product_by_attribute['title'] == product_by_major_type['title']:
                    temp_product_recommend.append(product_by_major_type)
                        
    #合并列表，去除重复   
    for product in temp_product_recommend:
        if not product in product_recommend:
            product_recommend.append(product)

    if node_id in PRODUCT_RECOMMEND and 'general' in PRODUCT_RECOMMEND:
        temp_product_recommend = []
        for product_by_attribute in PRODUCT_RECOMMEND[node_id]:
            for product_by_general in PRODUCT_RECOMMEND['general']:
                if product_by_attribute['title'] == product_by_general['title']:
                    temp_product_recommend.append(product_by_general)
                        
    #合并列表，去除重复   
    for product in temp_product_recommend:
        if not product in product_recommend:
            product_recommend.append(product)
    
    _temp_prodict_size = len(product_recommend)
    if size == None:
        size = 10 if _temp_prodict_size > 10 else _temp_prodict_size
    if size > _temp_prodict_size:
        return product_recommend
    else:
        return product_recommend[:size]

def _get_reason_by_nodeid(major, semester, node_list, deviation_dict):

    #获取专业大类
    if major in assess_student.MAJOR:
        major_type = assess_student.MAJOR[major]
    else:
        major_type = 'general'
    
    #结果字典
    result_dict = {}
    temp_result_dict = {}
    #学期（数字）转学期（中文）字典
    semester_dict = {1:'大一上学期', 2:'大一下学期', 3:'大二上学期', 4:'大二下学期', 5:'大三上学期', 6:'大三下学期'}
    #学期（数字）转年级（中文）字典
    grade_dict = {1:'大一', 2:'大一', 3:'大二', 4:'大二', 5:'大三', 6:'大三'}
    #专业分类（英文）转专业分类（中文）字典
    major_type_dict = {'commerce':'商科','liberal_arts':'文科','engineering':'工科','science':'理科','general':'所有专业'}
    
    if not major_type in REASON_DICT:
        major_type = 'general'
    
    if not major_type == 'general':
        for attribute in deviation_dict:
            if not 'special' in REASON_DICT[major_type]:
                break
            if attribute in REASON_DICT[major_type]['special']:
                deviation = deviation_dict[attribute]
                for row in REASON_DICT[major_type]['special'][attribute]:
                    if deviation >= float(row[0].split('-')[0]) and deviation <= float(row[0].split('-')[1]) and row[1].count(str(semester)) > 0:
                        result_dict[NODE_NAME_DICT[attribute]] = {}
                        result_dict[NODE_NAME_DICT[attribute]]['what'] = row[2].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                        result_dict[NODE_NAME_DICT[attribute]]['how'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
        #反转节点字典
        node_name_dict = dict((v,k) for k, v in NODE_NAME_DICT.items())
        
        #两项对比
        compare = list(map(lambda x:node_name_dict[x['nodeid']], node_list[:3]))
        
        if len(compare) >=2:
            success = 0
            if 'compare' in REASON_DICT[major_type]:
                #在前三项的第一项和第二项产生比较，必然第一项>第二项
                for row in REASON_DICT[major_type]['compare']:
                    if row[0] == compare[0]:
                        if row[1] == compare[1]:
                            if row[2].count(str(semester)) > 0:
                                result_dict[NODE_NAME_DICT[compare[0]]] = {}
                                result_dict[NODE_NAME_DICT[compare[0]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[0]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[1]]] = {}
                                result_dict[NODE_NAME_DICT[compare[1]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[1]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                success = 1
                if not success == 1 and len(compare) >= 3:
                    #第一项和第三项产生比较，必然第一项>第三项
                    for row in REASON_DICT[major_type]['compare']:
                        if row[0] == compare[0]:
                            if row[1] == compare[2]:
                                if row[2].count(str(semester)) > 0:
                                    result_dict[NODE_NAME_DICT[compare[0]]] = {}
                                    result_dict[NODE_NAME_DICT[compare[0]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[0]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[2]]] = {}
                                    result_dict[NODE_NAME_DICT[compare[2]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[2]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    success = 1           
                if not success == 1 and len(compare) >= 3:
                    #第二项和第三项产生比较，必然第二项>第三项
                    for row in REASON_DICT[major_type]['compare']:
                        if row[0] == compare[1]:
                            if row[1] == compare[2]:
                                if row[2].count(str(semester)) > 0:
                                    result_dict[NODE_NAME_DICT[compare[1]]] = {}
                                    result_dict[NODE_NAME_DICT[compare[1]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[1]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[2]]] = {}
                                    result_dict[NODE_NAME_DICT[compare[2]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    result_dict[NODE_NAME_DICT[compare[2]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                    
        if 'common' in REASON_DICT[major_type]:
            if 'priority_high' in REASON_DICT[major_type]['common']:
            #优先级高
                for node in node_list[:3]:
                    if node['nodeid'] in result_dict:
                        continue
                    if node_name_dict[node['nodeid']] in REASON_DICT[major_type]['common']['priority_high']:
                        result_dict[node['nodeid']] = {}
                        result_dict[node['nodeid']]['what'] = REASON_DICT[major_type]['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                        result_dict[node['nodeid']]['how'] = REASON_DICT[major_type]['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
            #优先级低
            if 'priority_low' in REASON_DICT[major_type]['common']:
                for node in node_list[3:]:
                    if node['nodeid'] in result_dict:
                        continue
                    if node_name_dict[node['nodeid']] in REASON_DICT[major_type]['common']['priority_low']:
                        result_dict[node['nodeid']] = {}
                        result_dict[node['nodeid']]['what'] = REASON_DICT[major_type]['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                        result_dict[node['nodeid']]['how'] = REASON_DICT[major_type]['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
    temp_result_dict = copy.deepcopy(result_dict)
    result_dict = {}
    #通用
    major_type = 'general'
    for attribute in deviation_dict:
        if not 'special' in REASON_DICT[major_type]:
            break
        if attribute in REASON_DICT[major_type]['special']:
            deviation = deviation_dict[attribute]
            for row in REASON_DICT[major_type]['special'][attribute]:
                if deviation >= float(row[0].split('-')[0]) and deviation <= float(row[0].split('-')[1]) and row[1].count(str(semester)) > 0:
                    result_dict[NODE_NAME_DICT[attribute]] = {}
                    result_dict[NODE_NAME_DICT[attribute]]['what'] = row[2].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                    result_dict[NODE_NAME_DICT[attribute]]['how'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
    #反转节点字典
    node_name_dict = dict((v,k) for k, v in NODE_NAME_DICT.items())

    #两项对比
    compare = list(map(lambda x:node_name_dict[x['nodeid']], node_list[:3]))
    if len(compare) >=2:
        success = 0
        if 'compare' in REASON_DICT[major_type]:
            #在前三项的第一项和第二项产生比较，必然第一项>第二项
            for row in REASON_DICT[major_type]['compare']:
                if row[0] == compare[0]:
                    if row[1] == compare[1]:
                        if row[2].count(str(semester)) > 0:
                            result_dict[NODE_NAME_DICT[compare[0]]] = {}
                            result_dict[NODE_NAME_DICT[compare[0]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                            result_dict[NODE_NAME_DICT[compare[0]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                            result_dict[NODE_NAME_DICT[compare[1]]] = {}
                            result_dict[NODE_NAME_DICT[compare[1]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                            result_dict[NODE_NAME_DICT[compare[1]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                            success = 1
            
            if not success == 1 and len(compare) >= 3:
                #第一项和第三项产生比较，必然第一项>第三项
                for row in REASON_DICT[major_type]['compare']:
                    if row[0] == compare[0]:
                        if row[1] == compare[2]:
                            if row[2].count(str(semester)) > 0:
                                result_dict[NODE_NAME_DICT[compare[0]]] = {}
                                result_dict[NODE_NAME_DICT[compare[0]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[0]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[2]]] = {}
                                result_dict[NODE_NAME_DICT[compare[2]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[2]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                success = 1
            if not success == 1 and len(compare) >= 3:
                #第二项和第三项产生比较，必然第二项>第三项
                for row in REASON_DICT[major_type]['compare']:
                    if row[0] == compare[1]:
                        if row[1] == compare[2]:
                            if row[2].count(str(semester)) > 0:
                                result_dict[NODE_NAME_DICT[compare[1]]] = {}
                                result_dict[NODE_NAME_DICT[compare[1]]]['what'] = row[3].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[1]]]['how'] = row[4].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[2]]] = {}
                                result_dict[NODE_NAME_DICT[compare[2]]]['what'] = row[5].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                                result_dict[NODE_NAME_DICT[compare[2]]]['how'] = row[6].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])                 
    if 'common' in REASON_DICT[major_type]:
        if 'priority_high' in REASON_DICT[major_type]['common']:
        #优先级高
            for node in node_list[:3]:
                if node['nodeid'] in result_dict:
                    continue
                if node_name_dict[node['nodeid']] in REASON_DICT[major_type]['common']['priority_high']:
                    result_dict[node['nodeid']] = {}
                    result_dict[node['nodeid']]['what'] = REASON_DICT[major_type]['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                    result_dict[node['nodeid']]['how'] = REASON_DICT[major_type]['common']['priority_high'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
        #优先级低
        if 'priority_low' in REASON_DICT[major_type]['common']:
            for node in node_list[3:]:
                if node['nodeid'] in result_dict:
                    continue
                if node_name_dict[node['nodeid']] in REASON_DICT[major_type]['common']['priority_low']:
                    result_dict[node['nodeid']] = {}
                    result_dict[node['nodeid']]['what'] = REASON_DICT[major_type]['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[0].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
                    result_dict[node['nodeid']]['how'] = REASON_DICT[major_type]['common']['priority_low'][node_name_dict[node['nodeid']]].split('|')[1].replace('{grade}',grade_dict[semester]).replace('{semester}',semester_dict[semester]).replace('{major_type}',major_type_dict[major_type])
    for nodeid in temp_result_dict:
        if nodeid in result_dict:
            result_dict[nodeid] = temp_result_dict[nodeid]
    return result_dict

def _get_nodes_products(part_score_dict, language_type, exam_type, size):

    unfinished_nodes_products = [] # 未完成任务结点（关联了相应的机会产品、项目）
    return_unfinished_nodes = [] # 未完成任务结点（存储的是结点ID）

    # 计算各个结点的权值，按照计算后的权重值对各个学习提升任务排序
    finished_nodes, unfinished_nodes, result_weight = _calculate_nodes_weight(part_score_dict, language_type, exam_type)
    if not 'activity' in unfinished_nodes:
        unfinished_nodes.append('activity')
        
    path_plan_logger.info('calculate_nodes_weight')
    for each in result_weight:
        if each[0] in unfinished_nodes:
            return_unfinished_nodes.append(NODE_NAME_DICT[each[0]])
    
    temp_list = []
    if 'gpa' in part_score_dict:
        temp_list.append('gpa')
    if 'ielts' in part_score_dict:
        temp_list.append('ielts')
    if 'toefl' in part_score_dict:
        temp_list.append('toefl')
    if 'gre' in part_score_dict:
        temp_list.append('gre')
    if 'gmat' in part_score_dict:
        temp_list.append('gmat')
    
    deviation_list = list(map(lambda x:{x:round(TARGET_DICT[part_score_dict['target']][x] - part_score_dict[x],2)},temp_list))
    deviation_dict = {}
    for node in deviation_list:
        for key in node:
            deviation_dict[key] = node[key]
    _temp_unfinished_nodes = list(map(lambda x:{'nodeid':x}, return_unfinished_nodes))
    for each in list(map(lambda x:{'nodeid': x['node_id']}, finished_nodes)):
        _temp_unfinished_nodes.append(each)
        
    #获取推荐理由
    reason_dict = _get_reason_by_nodeid(part_score_dict['real_major'],part_score_dict['grade'], _temp_unfinished_nodes, deviation_dict)

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
    elif language_type == 'neither':
        return_target_dict['language'] = {'type': 'TOEFL/IELTS', 'score': str(target['toefl'])+'/'+str(target['ielts'])}
    else:
        pass
    
    if exam_type in ['gre', 'gmat']:
        return_target_dict['exam'] = {'type': exam_type.upper(), 'score': target[exam_type]}
    elif exam_type == 'neither':
        return_target_dict['exam'] = {'type': 'GRE/GMAT', 'score': str(target['gre'])+'/'+str(target['gmat'])}
    else:
        pass
    return return_target_dict

def _check_schedule_size(size):
    if size == None:
        return size
    size = convert_to_int(size)
    if size < 1:
        raise ValueError('size应为大于0的整数')
    else:
        return size
# 写的很乱。需要重构
def _get_user_analysis(pre_handle_condition, after_handle_condition, target, language_type, exam_type):
    ''' 为用户返回咨询师提供的软性、硬性分析文案'''
    target = str(target)
    _temp_hard_cnt = ''
    _temp_soft_cnt = ''
    flag_soft = 1
    flag_hard = 1
    title_flag_soft = ''
    title_flag_hard = ''
    is_last = 0 
    for index, each in enumerate(ANALYSIS_TABLE):
        table_key = each[0]
        if language_type == 'toefl':
            if table_key[:5] == 'ielts':
                continue
        elif language_type == 'ietls':
            if table_key[:5] == 'toefl':
                continue
        elif language_type == 'none':
            if table_key[:5] == 'toefl' or table_key[:5] == 'ielts' :
                continue
        if exam_type == 'gre':
            if table_key[:4] == 'gmat':
                continue
        elif exam_type == 'gmat':
            if table_key[:3] == 'gre':
                continue
        elif exam_type == 'none':
            if table_key[:4] == 'gmat' or table_key[:3] == 'gre' :
                continue
        field_user = each[1]
        is_hard_condition = int(each[2])
        is_level_divide = int(each[3])
        default_level = each[4]
        if is_hard_condition == 1:
            if len(each) > 5:
                if flag_hard < 1:
                    flag_hard = 0
                    _temp_hard_cnt = _temp_hard_cnt.replace(title_flag_hard, '')+ '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    title_flag_hard = '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                else:
                    _temp_hard_cnt = _temp_hard_cnt  + '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    title_flag_hard = '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    flag_hard = 0
                
            if field_user.find('_') > 0:
                try:
                    _temp_field = float(after_handle_condition[field_user.split('_')[0]][field_user.split('_')[1]])
                except:
                    try:
                        _temp_field = float(pre_handle_condition[field_user.split('_')[0]][field_user.split('_')[1]])
                    except:
                        _temp_field = float(default_level)
            else:
                try:
                    _temp_field = float(pre_handle_condition[field_user])
                except:
                    _temp_field = float(default_level)
            if is_level_divide == 0:
                for each_record in USER_ANALYSIS[table_key]:
                    if float(each_record['min_value']) <= _temp_field <= float(each_record['max_value']):
                        if len(each_record['target'][target]) > 1:
                            _temp_hard_cnt = _temp_hard_cnt + '<p class="p1_Tde">'+each_record['target'][target]+'</p>'
                            flag_hard = flag_hard + 1
            else:
                _temp_field = convert_to_str(int(_temp_field))
                for each_record in USER_ANALYSIS[table_key]:
                    if _temp_field == each_record['level']:
                        if len(each_record['target'][target]) > 1:
                            _temp_hard_cnt = _temp_hard_cnt + '<p class="p1_Tde">'+each_record['target'][target]+'</p>'
                            flag_hard = flag_hard + 1
                       
        else:
            if is_last == 1 and field_user.split('_')[0] == 'internship':
                    continue
            if len(each) > 5:
                if flag_soft < 1:
                    flag_soft = 0
                    _temp_soft_cnt = _temp_soft_cnt.replace(title_flag_soft, '')+ '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    title_flag_soft = '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                else:
                    _temp_soft_cnt = _temp_soft_cnt  + '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    title_flag_soft = '<p class="p1_Tde" align="center">'+each[5]+'</p>'
                    flag_soft = 0
            if is_level_divide == 1:
                if field_user.find('_') > 0:
                    try:
                        _temp_field = str(after_handle_condition[field_user.split('_')[0]][field_user.split('_')[1]])
                    except:
                        _temp_field = str(default_level)
                else:
                    try:
                        _temp_field = str(after_handle_condition[field_user])
                    except:
                        _temp_field = str(default_level)
                _temp_field = _temp_field.replace('.0', '')
                for each_record in USER_ANALYSIS[table_key]:
                    if _temp_field == each_record['level']:
                        if len(each_record['target'][target]) > 1:
                            _temp_soft_cnt = _temp_soft_cnt + '<p class="p1_Tde">'+each_record['target'][target]+'</p>'
                            flag_soft = flag_soft + 1
                if _temp_field  == '5' and field_user == 'internship_duration':
                    is_last = 1

            if index == len(ANALYSIS_TABLE)-1:
                if flag_soft < 1:
                    _temp_soft_cnt = _temp_soft_cnt.replace(title_flag_soft, '')
    return {
        'hard_condition_analysis': _temp_hard_cnt.strip(),
        'soft_condition_analysis': _temp_soft_cnt.strip(),
    }

def schedule(condition, size=None):
    part_score_dict = {}
    try:
        #size 校对是否为大于0的整数
        size = _check_schedule_size(size)
        condition_copy = copy.deepcopy(condition)
   
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
        hard_condition = _get_hard_condition(student_info, language_type, exam_type)
        part_score_dict.update(hard_condition)
        path_plan_logger.info('[successed] _get_hard_condition()')
       
        #提取用户的软性指标（activity、 scholarship、 internship、 research、 credential、 competition）
        part_score_dict.update(_get_soft_condition(user_condition))
        path_plan_logger.info('[successed] _get_soft_condition()')

        # 为学习提升任务结点关联相应的机会产品
        finished_nodes, unfinished_nodes_products = _get_nodes_products(part_score_dict, language_type, exam_type, size)
        path_plan_logger.info('[successed] _get_nodes_products()')

        # 返回目标值
        return_target = _get_return_target(part_score_dict['target'], language_type, exam_type)
        path_plan_logger.info('[successed] _get_return_target()')

        # 返回软硬性条件分析文案
        try:
            user_analysis = _get_user_analysis(condition_copy['data'], student_info['data'], part_score_dict['target'], language_type, exam_type)
        except Exception as e:
            print('except:'+str(e))
    except Exception as e:
        file = open('err_log.txt', 'a', encoding='utf-8')
        file.write(str(e))
        file.write(str(condition)+'\n')
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
            'user_analysis':user_analysis,
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
    temp_dict = {}
    for major in assess_student.MAJOR:
        tag_list.append(major)
        tag_list.append(major+'_only')
        temp_dict[assess_student.MAJOR[major]] = ""
    for major_type in temp_dict:
        tag_list.append(major_type)
        
    tag_list.append('general')
    #从数据库中获取tag对应的id
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
        products_list = []
        for record in product_collection.find({'tag':{'$regex':tag_dict[tag_name]}, 'is_online':1, 'is_delete':0, 'is_status':0},{'id':1,'title':1,'title_pic':1,'tag':1}):
            product = {}
            try:
                product['product_id'] = record['id']
                product['title'] = record['title']
                product['picture'] = record['title_pic']
            except KeyError:
                continue
            products_list.append(product)
        PRODUCT_RECOMMEND[tag_name] = products_list
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
        #如果专业不在字典中则新建专业字典
        if not line[0] in REASON_DICT:
            REASON_DICT[line[0]] = {}
        #如果common在专业字典中
        if line[1] == 'common':
            if line[1] in REASON_DICT[line[0]]:
                #如果优先级在common字典中
                if line[2] in REASON_DICT[line[0]][line[1]]:
                    #则在优先级字典中加入key属性，并且给key复制
                    REASON_DICT[line[0]][line[1]][line[2]][line[3]] = line[4]+'|'+line[5]
                else:
                    REASON_DICT[line[0]][line[1]][line[2]] = {}
                    REASON_DICT[line[0]][line[1]][line[2]][line[3]] = line[4]+'|'+line[5]
            else:
                #common不在字典中则添加common
                REASON_DICT[line[0]][line[1]] = {}
                #添加优先级
                REASON_DICT[line[0]][line[1]][line[2]] = {}
                #添加key和value
                REASON_DICT[line[0]][line[1]][line[2]][line[3]] = line[4]+'|'+line[5]
        #如果special在专业字典中
        elif line[1] == 'special':
            if line[1] in REASON_DICT[line[0]]:
                if line[2] in REASON_DICT[line[0]][line[1]]:
                    REASON_DICT[line[0]][line[1]][line[2]].append(line[3:])
                else:
                    REASON_DICT[line[0]][line[1]][line[2]] = []
                    REASON_DICT[line[0]][line[1]][line[2]].append(line[3:])
            else:
                REASON_DICT[line[0]][line[1]] = {}
                REASON_DICT[line[0]][line[1]][line[2]] = []
                REASON_DICT[line[0]][line[1]][line[2]].append(line[3:])
        elif line[1] == 'compare':
            if line[1] in REASON_DICT[line[0]]:
                REASON_DICT[line[0]][line[1]].append(line[2:])
            else:
                REASON_DICT[line[0]][line[1]] = []
                REASON_DICT[line[0]][line[1]].append(line[2:])
    path_plan_logger.info('[successed] loading reason of different nodes from reason.csv to dict.')

def _load_user_analysis():
    path_plan_logger.info('[starting] loading userAnalysis information from mongodb . . . ')
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
    userAnalysis_collection = mongo_client.get_collection('userAnalysis')
    for each in userAnalysis_collection.find():
        try:
            _temp_analysis = []
            if each['type'] in USER_ANALYSIS:
                _temp_analysis = USER_ANALYSIS[each['type']]
            _temp_analysis.append(each)
            USER_ANALYSIS[each['type']] = _temp_analysis
        except Exception as e:
            path_plan_logger.error(e)
            path_plan_logger.error('some record invalid .')
            path_plan_logger.info('wrong record : %s ', str(each))
            return
    try:
        mongo_client.close() # 关闭连接
        path_plan_logger.info('close pymongo connection successed.')
    except Exception as e:
        path_plan_logger.error('close pymongo connection failed.')

def init():
    start_time = time.time()

    _logging_conf() #初始化日志设置

    path_plan_logger.info('[starting] ----------initializing----------')

    _load_node() # 加载每个学习提升任务对应数据库里的Node节点的ID

    _load_target() # 加载每个档次院校个学习提升任务的目标值
    
    _load_init_weight() # 加载各个专业的每个学期的学习提升任务的安排(按照咨询师给的初始权重值排序)
    
    _load_products_by_tag() # 从mongodb库里的product集合加载product信息,并按标签tag分类

    _load_reason() # 从配置文件[reason/reason.csv]中加载文案

    _load_user_analysis() # 从mongodb库里的userAnalysis集合里加载咨询师的软硬性分析文案
    
    path_plan_logger.info('[successed] ----------initializing----------')
