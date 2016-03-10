# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'
__doc__ = '''this py is used to schedule the timetable for those who want to study abroad,
                the input is the grade、 target school level、 condition of the user，
                the output is the schedule describing what they should prepare in different term'''
import json
import time

# 每个部分目标值
SEG_TARGET_DICT = {}

# 大一到大四13个时间段每个时间段可以完成的目标
TERM_NODE_DICT = {}

# 初始化目标内容集合
NODE_LIST = list()

# 获取当前时间段
def get_start_term(grade='大二'):
    # 获取当前的月份
    now_month = int(time.strftime('%m', time.localtime(time.time())))
    if 1 <= now_month <= 2:
        increase = 1
    elif 3 <= now_month <= 6:
        increase = 2
    elif 7 <= now_month <= 8:
        increase = 3
    elif 9 <= now_month <= 12:
        increase = 0
    else:
        increase = 0

    if grade == '大一':
        grade = 1 + increase
    elif grade == '大二':
        grade = 5 + increase
    elif grade == '大三':
        grade = 9 + increase
    elif grade == '大四':
        grade = 13 + increase
    else:
        grade = 1
    return grade

def node_filter(condition, nodestr, target_level=2):
    node_list = list(map(lambda x: int(x), nodestr.split('-')))
    if float(condition['gpa']) >= SEG_TARGET_DICT['gpa'][str(target_level)]:
        if 1 in node_list:
            node_list.remove(1)
    if float(condition['toefl']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
        if 3 in node_list:
            node_list.remove(3)
        if 4 in node_list:
            node_list.remove(4)
    if float(condition['gre']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
        if 2 in node_list:
            node_list.remove(2)
    return node_list

def schedule_debug(condition, grade='大一', target_level=2):
    grade = get_start_term(grade)
    return_dict = {}
    print 'grade %d ' % grade
    print TERM_NODE_DICT[grade]
    if 1 <= grade <= 7:
        node_temp_dict = eval(TERM_NODE_DICT[grade])
        for each in node_temp_dict:
            node_temp_dict[each] = node_filter(condition, node_temp_dict[each], target_level)
    #return_dict = sorted(node_temp_dict.items(), key=lambda x: x[0], reverse=True)
    for each in range(grade, 15):
        print each
        return_dict[each] = node_temp_dict[each]
    for each in return_dict:
        print each

    return return_dict

def schedule(condition, grade='大一', target_level=2):
    grade = get_start_term(grade)
    print 'grade %d' % grade
    print 'before :list:', NODE_LIST
    print json.dumps(SEG_TARGET_DICT, indent=4)
    # 将已经达到目标的节点移除掉
    if float(condition['gpa']) >= SEG_TARGET_DICT['gpa'][str(target_level)]:
        NODE_LIST.remove(1)
    if float(condition['toefl']) >= SEG_TARGET_DICT['toefl'][str(target_level)]:
        NODE_LIST.remove(3)
        NODE_LIST.remove(4)
    if float(condition['gre']) >= SEG_TARGET_DICT['gre'][str(target_level)]:
        NODE_LIST.remove(2)
    for each in range(1, grade):
        del TERM_NODE_DICT[str(each)]
    print 'after list:', NODE_LIST

def __init__():
    for each in open('resource/schedule/target.csv', 'r').readlines():
        each = each.strip('\r').strip('\n')
        # print each
        target_name = each.split(',')[0]
        target_level = str(each.split(',')[1])
        target_score = float(each.split(',')[2])
        if target_name in SEG_TARGET_DICT:
            SEG_TARGET_DICT[target_name].update({target_level: target_score})
        else:
            SEG_TARGET_DICT.update({target_name: {target_level: target_score}})
    for each in open('resource/schedule/schedule.csv', 'r').readlines():
        if each[0] == '#':
            continue
        each = each.strip('\r').strip('\n')
        TERM_NODE_DICT[int(each[:2])] = each[3:]


    # for each in open('resource/schedule/content.csv', 'r').readlines():
    #     if each[0] == '#':
    #         continue
    #     each = each.strip('\r').strip('\n').split('//')[0]
    #     node = str(each.split(',')[0])
    #     term = each.split(',')[1]
    #     necessary = int(each.split(',')[2])
    #
    #     # 初始化NODE节点集合
    #     NODE_LIST.append(int(node))
    #
    #     for each_term in term.split('-'):
    #         if each_term in TERM_NODE_DICT:
    #             node_list = TERM_NODE_DICT[each_term]
    #         else:
    #             node_list = list()
    #         node_list.append(node)
    #         TERM_NODE_DICT[each_term] = node_list
        #TERM_NODE_DICT = sorted(TERM_NODE_DICT.items(), key=itemgetter(0))
__init__()
test_dict = {
    'gpa': 3.6,
    'toefl': 105,
    'gre': 328,
}

schedule_debug(test_dict, '大二', 2)
# if __name__ == '__main__':
#     print 'starting . . . '
#
#     print 'exit . . . '
#get_start_term('大一')
# print json.dumps(TERM_NODE_DICT, indent=4)
#print json.dumps(sorted(TERM_NODE_DICT.items(), key=itemgetter(0)), indent=4)