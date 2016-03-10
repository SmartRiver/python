#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this py is used to search schools related to the user input.
				Optional parameter includes area 、 major.'''

import time
import common_func
from common_func import exit_error_func, convert_to_str
import logging
import sys
import json
import pymongo
from pymongo import MongoClient
from db_util import *
import logging
import logging.config

class SchoolTree(object):
    '''构建的院校的字典前缀树'''
    def __init__(self):
        self.root  = Node()  # Trie树root节点引用

    def add(self, word):
        ''' 添加字符串 '''
        word_display = word.split('|')[1]
        word_search = word.split('|')[0]
        university_area = word.split('|')[2]
        university_type = word.split('|')[3]
        university_weight = word.split('|')[4][:1]

        node = self.root
        for c in word_search:
            pos = self.find(node, c)
            if pos < 0:
                node.childs.append(Node(c))
                '''为了图简单，这里直接使用Python内置的sorted来排序
                pos有问题，因为sort之后的pos会变掉,所以需要再次find来获取真实的pos
                自定义单字符数组的排序方式可以实现任意规则的字符串数组的排序'''
                node.childs = sorted(node.childs, key=lambda child: child.c)
                pos = self.find(node, c)
            node = node.childs[pos]
        node.word = word_display
        node.university_type = university_type
        node.area = university_area
        node.weight = university_weight

    def preOrder(self, node):
        '''先序输出'''
        results = []
        if node.word:
            word = {
                'result': node.word+'|'+node.area+'|'+node.university_type,
                'weight': int(node.weight)
            }
            results.append(str(word))
        for child in node.childs:
            results.extend(self.preOrder(child))

        return results

    def find(self, node, c):
        '''查找字符插入的位置'''
        childs = node.childs
        _len = len(childs)
        if _len == 0:
            return -1
        for i in range(_len):
            if childs[i].c == c:
                return i
        return -1

    def setWords(self, words):
        for word in words:
            self.add(word)

    # 查询指定字符在构建的前缀树里的位置，并返回把它作为前缀的所有字符串
    def search(self, node, word):
        result = []
        _len = len(word)

        for each_node in node.childs:
            if each_node.c == word[0]:
                if _len == 1:
                    return self.preOrder(each_node)
                else:
                    result.extend(self.search(each_node, word[1:]))

        return result


class Node(object):
    def __init__(self, c=None, word=None, university_type=None, area=None, university_weight=None):
        self.c          = c    # 节点存储的单个字符
        self.word       = word # 节点存储的用于展示的大学名
        self.university_type       = university_type # 节点存储的大学的类型
        self.area       = area # 节点存储的大学所在的地区（国内精确到省份，国外只精确国家）
        self.weight     = university_weight # 节点存储的大学的权重值
        self.childs     = []   # 此节点的子节点

global search_logger # 日志

UNIVERSITY_LIST = [] # 学校库的字典

SCHOOL_TRIE = SchoolTree() # 学校库的前缀树

SCHOOL_SPECIAL_MAJOR = {} #综合前十或者专业优势

def _school_filter_by_country(search_result, country):
    '''如果指定国家，则只显示匹配到该国家的院校'''
    if country == None:
        return search_result
    country = country.lower()
    return list(filter(lambda x : eval(x)['result'].split('|')[1] == country, search_result))


def _sorted_school_weight(result):
    ''' 将匹配到的院校集合按照档次权重值排序'''
    return_result = []
    result_school_dict = {}
    for each in result:
        each = eval(each)
        result_school_dict[each['result']] = each['weight']
    for each in sorted(result_school_dict.items(), key=lambda x:x[1], reverse=False):
        return_result.append(each[0])
    return return_result

def _school_filter_by_major(result, major):
    ''' 如果是该专业的优势学校，并且不是清华北大，则变成'综合前十或者专业优势学校' '''
    for index,item in enumerate(result):
        if item.split('|')[0] in SCHOOL_SPECIAL_MAJOR[major]:
            if item.split('|')[2] != '清华北大':
                result[index] = item.split('|')[0] + '|' + item.split('|')[1] + '|综合前十或专业优势'

def _school_sort_by_area(search_result, area=None):
    '''如果指定地区，则将该地区匹配到的院校优先排列'''
    result = []
    for each in search_result:
        each = eval(each)
        if each['result'].split('|')[1] == area:
            result.insert(0, str(each))
        else:
            result.append(str(each))
    return result

def search_school(condition, major=None, area=None, country=None):
    ''' 学校查找'''
    if condition == '':
        return{
            'status': 'success',
            'result': [],
        }
    try:
        global SCHOOL_TRIE
        search_result = SCHOOL_TRIE.search(SCHOOL_TRIE.root, condition.lower())
    except:
        search_logger.error('no normal result returns .')
        return exit_error_func(3, 'condition: %s' % condition)

    # 去重
    search_result_set = set()
    for each in search_result:
        search_result_set.add(each)

    result = _school_filter_by_country(search_result_set, country=country) # 如果指定国家，则只显示匹配到该国家的院校

    if area != None:
        result = _school_sort_by_area(result, area=area) # 如果指定地区，则将该地区匹配到的院校优先排列

    result = _sorted_school_weight(result) # 将匹配到的院校集合按照档次权重值排序

    if len(result) > 10: # 如果结果院校数量大于10个，则取前10个返回
        result = result[:10]

    if major not in SCHOOL_SPECIAL_MAJOR:
        major = None
    if major != None:
        _school_filter_by_major(result, major=major) # 如果是该专业的优势学校，并且不是清华北大，则变成'综合前十或者专业优势学校'

    return{
        'status': 'success',
        'result': result,
    }

def _logging_conf():
    '''日志配置'''
    try:
        global search_logger
        logging.config.fileConfig('./conf/logging.conf')
        search_logger = logging.getLogger('general')
        search_logger.info('--------logging configurating success--------')
    except Exception as e:
        print('--------logging configurating failed--------')
    
def init(dict_from='mongodb'):
    '''初始化'''

    start_time = time.time()
    _logging_conf()
    search_logger.info('----------initializing----------')
    search_logger.info('type of reload : %s' % dict_from)
    try:
        for each in open('resource/school/special_school.txt', 'r', encoding='utf-8').readlines():
            try:
                each = each.strip('\r').strip('\n').strip()
                if each[:1] == '#':
                    major_key = each[1:]
                    SCHOOL_SPECIAL_MAJOR[major_key] = []
                else:
                    major_list = SCHOOL_SPECIAL_MAJOR[major_key]
                    major_list.append(each)
                    SCHOOL_SPECIAL_MAJOR[major_key] = major_list
            except:
                search_logger.error('some line is wrong when reading special school.')
                search_logger.info('wrong line : %s ', each)
                return
    except FileNotFoundError:
        search_logger.error('File resource/school/special_school.txt not found . . . ')
    # 学校库来自配置的文本文件
    if dict_from == 'conf':
        search_logger.info('school configuration from conf.txt.')
        try:
            for each in open('resource/university_dict.txt', 'r', encoding='utf-8').readlines():
                try:
                    each = each.strip('\r').strip('\n').lower()
                    UNIVERSITY_LIST.append(each)
                except:
                    search_logger.error('some line is wrong when convent to dict .')
                    search_logger.info('wrong line : %s ', each)
                    return
        except FileNotFoundError:
            search_logger.error('File resource/university_dict.txt not found . . . ')

    # 学校库来自mongodb库
    elif dict_from == 'mongodb':
        search_logger.info('school configuration from mongodb.')
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
                    search_logger.error(e)
                    search_logger.error('some line is wrong when read .')
                    search_logger.info('wrong line : %s ', each)
                    return
        except FileNotFoundError:
            search_logger.error('File resource/db.conf not found . . . ')
            return exit_error_func(3)
        except Exception as e:
            search_logger.error(e)
            search_logger.error('configuration failed.')

        mongo_client = MongoDB(host=url, port=port, username=username, password=password, auth=True)
        school_search_collection = mongo_client.get_collection('school', 'dulishuo')
        for each in school_search_collection.find():
            try:
                UNIVERSITY_LIST.append(each['display_name'].lower()+'|'+each['origin_name']+'|'+each['area'].lower()+'|'+str(each['type']).replace('.0','')+'|'+str(each['weight']))

            except TypeError as e:
                search_logger.error(e)
                search_logger.error('wrong line when converting：%s' % each)

        school_load_time = time.time()
        search_logger.info('ending reading data from mongodb，use time %f s.' % (school_load_time-start_time))
        try:
            mongo_client.close() # 关闭连接
            search_logger.info('close pymongo connection successed.')
        except Exception as e:
            search_logger.error('close pymongo connection failed.')
        
    else:
        search_logger.error('initializing failed，wrong params： %s' % dict_from)
        return exit_error_func(2, dict_from)

    # 构建学校库的前缀树
    global SCHOOL_TRIE
    SCHOOL_TRIE.setWords(UNIVERSITY_LIST)
    dict_tree_time = time.time()
    search_logger.info('completing building trie，use time %f s.' % (dict_tree_time-start_time))
    search_logger.info('----------initializing successed----------')

if __name__ == '__main__':
    init(dict_from='mongodb')
    condition = '华'
    area = 'general'
    major = '经济学'
    print(json.dumps(search_school(condition=condition, major=major, area=area), ensure_ascii=False, indent=4))

    #mon = MongoDB('123.57.250.189',27017,'dulishuo','Dulishuo123')
    #mon = MongoDB('123.57.250.189',27017)

    #dd = mon.get_collection('institute','dulishuo')
    #for each in dd.find():
        #print(str(type(each)))
    #mon =   MongoDB()d.next
    #print(mon.get_database('jianzhi'))
    #coll = mon.get_collection('test', 'test')
    #print(coll.find_one({'name': 'tim'}))
