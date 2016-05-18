import os
import copy
import json
from common_func import exit_error_func

WEIGHT = {} #各个专业的权重映射表
RULE = {}   #各个专业的晕眩运算规则
TRANSLATE = {} #学校与标识之间的映射
MAX = {}    #储存各个专业所有属性的最高值
MAJOR = {}  #储存所有专业和其分类

#-------------------------------------------初始化---------------------------------------------------
#初始化程序，将配置文件载入全局字典
def init():
    #读取学校和标识之间的映射关系
    load_translate()
    load_major()
    major = ""
    #遍历resource\assess_rule下所有文件
    dirs = os.walk('resource'+os.sep+'assess_rule')
    for root, path, files in dirs:
        print(path)
        for file in files:
            if not major == root.split(os.sep)[-1]:
                major = root.split(os.sep)[-1]
                #将所有专业的配置文件载入
                load_config(major)
                
#读取每个专业的配置文件
def load_config(major):
    #载入该major权值映射关系
    WEIGHT[major] = load_weight(major)
    #载入该major计算规则
    RULE[major] = load_rule(major)
    #载入该major权值最大值
    MAX[major] = load_max(WEIGHT[major])
    
def load_weight(major):
    weight = {}
    file = open('resource'+os.sep+'assess_rule'+os.sep+major+os.sep+'weight.csv', 'r', encoding='utf-8')
    title = ''
    #遍历文件
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        #清除空格将每项转为列表项，一行为一个完整的列表
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        tmp_title = line[0]
        #确定key值title，如果title已经存在，则直接将该行列表存入key值所对应的字典，其中，列表的key值为范围
        #如果title不存在，将key值置入weight字典，然后将该行列表存入key值所对应的字典，其中，列表的key值为范围
        if not tmp_title == title:
            title = tmp_title
            weight[title] = {}
            weight[title][line[2]] = line
        weight[title][line[2]] = line
    return weight

def load_rule(major):
    rule = []
    file = open('resource'+os.sep+'assess_rule'+os.sep+major+os.sep+'rule.csv', 'r', encoding='utf-8')
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        #清除空格将每项转为列表项，一行为一个完整的列表
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        #将该列表置入新的列表之中
        rule.append(line)
    return rule
    
def load_max(weight_dict):
    max = {}
    max_value = 0
    #根据该专业的权值映射字典，遍历各项所有权值，得到一个该项权值最大值字典
    for key in weight_dict:
        max_value = 0
        for sub_key in weight_dict[key]:
            if max_value < float(weight_dict[key][sub_key][1]):
                max_value = float(weight_dict[key][sub_key][1])
        max[key] = '%.2f'%max_value
    return max
    
def load_translate():
    file = open('resource'+os.sep+'translate.csv', 'r', encoding='utf-8')
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        #遍历翻译文件，将学校名和代号载入字典
        TRANSLATE[line[0]] = line[1]

def load_major():
    value = ''
    try:
        file = open('resource'+os.sep+'major.csv', 'r', encoding='utf-8')
    except Exception as e:
        print(e)
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        if line[0][0] == '*':
            value = line[0][1:]
        else:
            MAJOR[line[0]] = value
            
#---------------------------------------------初始化结束----------------------------------------------------- 



#--------------------------------------------评估一个学生----------------------------------------------------
def assess(student_info):
    major = ''
    #学生结果字典
    result = {}
    #满分结果字典
    result_full = {}
    try:
        #检测第一层键是否齐全，不齐全则抛出异常，因为之后的规划没法做了
        if 'major' in student_info.keys():
            major = student_info['major']
        else:
            raise Exception('传入的学生信息没有键值"major"，请重新检查学生信息结构')
        if not 'target' in student_info.keys():
            raise Exception('传入的学生信息没有键值"target"，请重新检查学生信息结构')
        if not 'grade' in student_info.keys():
            raise Exception('传入的学生信息没有键值"grade"，请重新检查学生信息结构')
        if not 'data' in student_info.keys():
            raise Exception('传入的学生信息没有键值"data"，请重新检查学生信息结构')
        
        #匹配专业，如果没有具体的评估规则，则将major转为general进行评估
        if not major in MAJOR:
            major = 'general'
        else:
            if not major in WEIGHT.keys():
                major = MAJOR[major]
        if not 'reletter' in student_info['data'].keys():
            student_info['data']['reletter'] = {}
            student_info['data']['reletter']['level'] = ['3','3','3']
        if not 'credential' in student_info['data']:
            student_info['data']['credential'] = {}
            student_info['data']['credential']['level'] = "2"
            
        #将学生信息中的有效项根据权值映射关系替换为为权值，剔除无效项
        student_weight_data = map_weight(student_info, WEIGHT[major], major)

        #根据学生信息的有效项和该专业的运算规则，进行结果计算，并返回结果
        result = exec_rule(student_weight_data, RULE[major])

        #将学生信息中的有效项根据权值映射关系替换为权值最大值
        student_weight_full_data = fill_with_full(copy.deepcopy(student_info['data']), MAX[major])

        #获得根据各项权值最大值计算的结果
        result_full = exec_rule(student_weight_full_data, RULE[major])

    except Exception as e:
        return exit_error_func(1, '接口调用失败，错误信息：\n'+str(e))

    result['dimension_full'] = result_full['dimension']
    result['result_full'] = result_full['result']
    result['student_info'] = student_info
    return {
        'status': 'success',
        'result': result
    }


def map_weight(student_info, weight_dict, major):
    student_data = student_info['data']
    new_student_data = {}
    new_student_weight_data = {}

    if not 'gpa' in student_data.keys():
        raise Exception('学生信息键"data"对应的字典缺少键"gpa"')
    if not 'school' in student_data['gpa'].keys():
        raise Exception('学生信息键"data"对应的字典中的键"gpa"对应的字典缺少键"school"')
    
    if not student_data['gpa']['school'].count('|') == 2:
        student_data['gpa']['school'] = '12'
    else:
        if not student_data['gpa']['school'].split('|')[2] in TRANSLATE.keys():
            student_data['gpa']['school'] = '12'
        else:
            student_data['gpa']['school'] = TRANSLATE[student_data['gpa']['school'].split('|')[2]]
    for key in weight_dict:
        main_key = key.split('_')[0] #第一层的键
        sub_key = key.split('_')[1]  #第二层的键
        #如果student_data有第一层相应键
        if main_key in student_data:
            if not main_key in new_student_weight_data: 
                new_student_weight_data[main_key] = {}
            if not main_key in new_student_data: 
                new_student_data[main_key] = {}
            #如果student_data有第二层相应键
            if sub_key in student_data[main_key]:
                if len(student_data[main_key][sub_key]) == 0 and not isinstance(student_data[main_key][sub_key], list):
                    new_student_data[main_key][sub_key] = '0'
                else:
                    new_student_data[main_key][sub_key] = student_data[main_key][sub_key]
                #判断值是否为列表（推荐信）
                #如果值是列表
                if isinstance(student_data[main_key][sub_key],list):
                    value_list = student_data[main_key][sub_key]
                    #列表长度不为零则将三个数相加
                    if not len(value_list) == 0:
                        value = 0
                        for sub_value in value_list:
                            for value_range in weight_dict[key]:
                                sub_value = float(sub_value)
                                min = float(value_range.split('-')[0])
                                max = float(value_range.split('-')[1])
                                if sub_value < max and sub_value >= min:
                                    value += float(weight_dict[key][value_range][1])
                                    break
                        new_student_weight_data[main_key][sub_key] = '%.2f'%value
                    #列表长度为零则将reletter的权值设置为0
                    else:
                        new_student_weight_data[mian_key][sub_key] = '0'
                #如果值不是列表
                else:
                    #如果值的字符串长度为0
                    if len(student_data[main_key][sub_key]) == 0:
                        #设置权值为0
                        new_student_weight_data[main_key][sub_key] = '0'
                    else:
                        #如果值的字符串长度不为0
                        #匹配相应的权值
                        success = 0
                        for value_range in weight_dict[key]:
                            value = float(student_data[main_key][sub_key])
                            min = float(value_range.split('-')[0])
                            max = float(value_range.split('-')[1])
                            #如果找到对应的权值
                            if value < max and value >= min:
                                new_student_weight_data[main_key][sub_key] = weight_dict[key][value_range][1]
                                success = 1
                                break
                        #如果没有找到相应的值
                        if success == 0:
                            raise Exception('学生信息键"data"对应的字典中的键"'+main_key+'"对应的字典的键"'+sub_key+'"的值无法匹配到相应权值')
            else:
                raise Exception('学生信息键"data"对应的字典中的键"'+main_key+'"对应的字典缺少键"'+sub_key+'"')
        else:
            raise Exception('学生信息键"data"对应的字典缺少键："'+main_key+'"')
    student_info['data'] = new_student_data
    return new_student_weight_data

def fill_with_full(student_data_copy, max):
    for key in max:
        student_data_copy[key.split('_')[0]][key.split('_')[1]] = max[key]
    return student_data_copy
    
def exec_rule(student_data, rule_dict):
    student_data_copy = copy.deepcopy(student_data)
    cache_dict = {}  #储存各类运算结果的临时字典
    result_dict = {} #储存最终结果的字典
    dimension_dict = {}
    for rule in rule_dict:
        if rule[1] == 'multi':
            key = rule[0]
            value = 1
            for element in rule[2:]:
                if element[0] == '%':
                    element = element[1:]
                    if element in cache_dict.keys():
                        value *= float(cache_dict[element])
                    else:
                        value *= float(student_data[element.split('_')[0]][element.split('_')[1]])
                else:
                    value *= float(element)
            cache_dict[key] = '%.2f'%value
        elif rule[1] == 'sum':
            key = rule[0]
            value = 0
            for element in rule[2:]:
                if element[0] == '%':
                    element = element[1:]
                    if element in cache_dict.keys():
                        value += float(cache_dict[element])
                    else:
                        value += float(student_data[element.split('_')[0]][element.split('_')[1]])
                else:
                    value += float(element)
            cache_dict[key] = '%.2f'%value
        elif rule[1] == 'max':
            key = rule[0]
            value = 0
            for element in rule[2:]:
                if element[0] == '%':
                    element = element[1:]
                    if element in cache_dict.keys():
                        if float(cache_dict[element]) > value:
                            value = float(cache_dict[element])
                    else:
                        if float(student_data[element.split('_')[0]][element.split('_')[1]]) > value:
                            value = float(student_data[element.split('_')[0]][element.split('_')[1]])
                else:
                    if float(element) > value:
                        value = float(element)
            cache_dict[key] = '%.2f'%value
        elif rule[1] == 'range':
            if float(cache_dict[rule[3][1:]]) >= float(rule[4]) and float(cache_dict[rule[3][1:]]) < float(rule[5]):
                cache_dict[rule[0]] = '%.2f'%float(rule[2])
        elif rule[1] == 'dimension':
            key = rule[0]
            value = 0
            for element in rule[2:]:
                if element[0] == '%':
                    element = element[1:]
                    if element in cache_dict.keys():
                        value += float(cache_dict[element])
                    else:
                        value += float(student_data[element.split('_')[0]][element.split('_')[1]])
                else:
                    value += float(element)
            dimension_dict[key] = '%.2f'%value
        else:
            pass
    #neither 都没有考
    #none 都没有该结构
    language_type = ''
    exam_type = ''
    if 'ielts' in cache_dict.keys() and 'toefl' in cache_dict.keys():
        if float(cache_dict['ielts']) > float(cache_dict['toefl']):
            language_type = 'ielts'
        else:
            language_type = 'toefl'
        if float(cache_dict['ielts']) == 0 and float(cache_dict['toefl']) == 0:
            language_type = 'neither'
    elif 'ielts' in cache_dict.keys():
        language_type = 'ielts'
    elif 'toefl' in cache_dict.keys():
        language_type = 'toefl'
    else:
        language_type = 'none'
        
    if 'gre_factor' in cache_dict.keys() and 'gmat_factor' in cache_dict.keys():
        if float(cache_dict['gre_factor']) > float(cache_dict['gmat_factor']):
            exam_type = 'gre'
        else:
            exam_type = 'gmat'
        if float(cache_dict['gre_factor']) == 0 and float(cache_dict['gmat_factor']) == 0:
            exam_type = 'neither'
    elif 'gre_factor' in cache_dict.keys():
        exam_type = 'gre'
    elif 'gmat_factor' in cache_dict.keys():
        exam_type = 'gmat'
    else:
        exam_type = 'none'
        
    return {
        'dimension': dimension_dict,
        'result': cache_dict['result'],
        'language_type': language_type,
        'exam_type': exam_type,
        'level': int(float(cache_dict['level']))
    }
