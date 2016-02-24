import os
import copy
import json

WEIGHT = {} #各个专业的权重映射表
RULE = {}   #各个专业的晕眩运算规则
TRANSLATE = {} #学校与标识之间的映射
MAX = {}    #储存各个专业所有属性的最高值

#-------------------------------------------初始化---------------------------------------------------
#初始化程序，将配置文件载入全局字典
def init():
    #读取学校和标识之间的映射关系
    load_translate()
    major = ""
    #遍历resource\assess_rule下所有文件
    dirs = os.walk('resource\\assess_rule')
    for root, path, files in dirs:
        for file in files:
            if not major == root.split('\\')[-1]:
                major = root.split('\\')[-1]
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
    file = open('resource/assess_rule/'+major+'/weight.csv', 'r', encoding='utf-8')
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
    file = open('resource/assess_rule/'+major+'/rule.csv', 'r', encoding='utf-8')
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
    file = open('resource/translate.csv', 'r', encoding='utf-8')
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        #遍历翻译文件，将学校名和代号载入字典
        TRANSLATE[line[0]] = line[1]
#---------------------------------------------初始化结束----------------------------------------------------- 



#--------------------------------------------评估一个学生----------------------------------------------------
def assess_student(student_info):
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
            raise Exception('传入的学生信息没有键值"major"，请重新检查学生信息结构'+'\n'+json.dumps(student_info, indent=4))
        if not 'target' in student_info.keys():
            raise Exception('传入的学生信息没有键值"target"，请重新检查学生信息结构'+'\n'+json.dumps(student_info, indent=4))
        if not 'grade' in student_info.keys():
            raise Exception('传入的学生信息没有键值"grade"，请重新检查学生信息结构'+'\n'+json.dumps(student_info, indent=4))
        if not 'data' in student_info.keys():
            raise Exception('传入的学生信息没有键值"data"，请重新检查学生信息结构'+'\n'+json.dumps(student_info, indent=4))   
            
        #为student_info创建一个副本，保留原始数据
        student_info_copy = copy.deepcopy(student_info)
        
        #匹配专业，如果没有具体的评估规则，则将major转为general进行评估
        if not major in WEIGHT.keys():
            major = 'general'
        
        #将学生信息中的有效项根据权值映射关系替换为为权值，剔除无效项
        map_weight(student_info['data'], WEIGHT[major], major)
        
        #根据学生信息的有效项和该专业的运算规则，进行结果计算，并返回结果
        result = exec_rule(student_info['data'], RULE[major])
        
        #将学生信息中的有效项根据权值映射关系替换为权值最大值
        fill_with_full(student_info['data'], MAX[major])
        
        #获得根据各项权值最大值计算的结果
        result_full = exec_rule(student_info['data'], RULE[major])
    except Exception as e:
        return '接口调用失败，错误信息：\n'+str(e)

    result['dimension_full'] = result_full['dimension']
    result['result_full'] = result_full['result']
    result['student_info'] = student_info_copy
    file = open('output.txt','w',encoding='utf-8')
    file.write(json.dumps(result, indent=4))
    return result
    
def map_weight(student_data, weight_dict, major):
    student_data['gpa']['school'] = TRANSLATE[student_data['gpa']['school'].split('|')[2]]
    for key in weight_dict:
        if not key.count('_') == 1:
            raise Exception('权值映射文件'+major+'/weight.csv中的'+key+'结构错误，应该包含一个下划线')
        main_key = key.split('_')[0]
        sub_key = key.split('_')[1]
        if main_key in student_data:
            if sub_key in student_data[main_key]:
                if isinstance(student_data[main_key][sub_key],list):
                    value_list = student_data[main_key][sub_key]
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
                        student_data[main_key][sub_key] = '%.2f'%value
                else:
                    for value_range in weight_dict[key]:
                        value = float(student_data[main_key][sub_key])
                        min = float(value_range.split('-')[0])
                        max = float(value_range.split('-')[1])
                        if value < max and value >= min:
                            student_data[main_key][sub_key] = weight_dict[key][value_range][1]
                            break
            else:
                raise Exception(main_key+'：缺少键值'+sub_key)
        else:
            raise Exception('缺少键值：'+main_key)

def fill_with_full(student_data_copy, max):
    for key in max:
        student_data_copy[key.split('_')[0]][key.split('_')[1]] = max[key]
    
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
    language_type = ''
    exam_type = ''
    if float(cache_dict['ielts']) > float(cache_dict['toefl']):
        language_type = 'ielts'
    else:
        language_type = 'toefl'
    if float(cache_dict['ielts']) == 0 and float(cache_dict['toefl']) == 0:
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
        'dimension':dimension_dict,
        'result':cache_dict['result'],
        'language_type':language_type,
        'exam_type':exam_type,
        'level':'%d'%int(float(cache_dict['level']))
    }

init()