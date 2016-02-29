import os
def get_reason_by_nodeid(grade, node_list, node_name_dict):
    init()
    result_dict = {}
    grade_dict = {'1':'大一','2':'大一','3':'大二','4':'大二','5':'大三','6':'大三'}
    if grade in grade_dict:
        grade = grade_dict[grade]
    else:
        raise Exception('no such grade')
    node_name_dict = dict((v,k) for k, v in node_name_dict.items())
    #优先级高
    for node in node_list[:3]:
        result_dict[node['nodeid']] = REASON_DICT['common']['priority_high'][node_name_dict[node['nodeid']]].replace('{grade}',grade)
    for node in node_list[3:]:
        result_dict[node['nodeid']] = REASON_DICT['common']['priority_low'][node_name_dict[node['nodeid']]].replace('{grade}',grade)     
    return result_dict
    
    
def init():
    global REASON_DICT
    REASON_DICT = {}
    file = open('resource'+os.sep+'reason'+os.sep+'reason.csv', 'r', encoding='utf-8')
    while 1:
        line = file.readline()
        if not line:
            break
        if len(line.strip('\n').strip()) == 0 or line.strip('\n').strip()[0] == '#':
            continue
        line = list(map(lambda column: column.strip('\n').strip(), line.split(',')))
        if line[0] == 'common':
            if line[0] in REASON_DICT:
                if line[1] in REASON_DICT[line[0]]:
                    REASON_DICT[line[0]][line[1]][line[2]] = line[3]
                else:
                    REASON_DICT[line[0]][line[1]] = {}
                    REASON_DICT[line[0]][line[1]][line[2]] = line[3]
            else:
                REASON_DICT[line[0]] = {}
                REASON_DICT[line[0]][line[1]] = {}
                REASON_DICT[line[0]][line[1]][line[2]] = line[3]