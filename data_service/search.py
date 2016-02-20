#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'xiaohe'
__doc__     = '''this py is used to search schools related to the user input.
				Optional parameter includes area, which means the area user in.'''

import time
import common_func
from common_func import exit_error_func, convert_to_str
import logging
import sys
import json
import pymongo
from pymongo import MongoClient
from db_util import *




class SchoolTree(object):
    def __init__(self):
        self.root  = Node()  # Trie树root节点引用

    def add(self, word):
        ''' 添加字符串 '''
        word_display = word.split('|')[1]
        word_search = word.split('|')[0]
        university_area = word.split('|')[2]
        university_type = word.split('|')[3]
        #university_weight = word.split('|')[4]

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
        #node.weight = university_weight

    def preOrder(self, node):
        '''先序输出'''
        results = []
        if node.word:
            results.append({'area': node.area, 'result': node.word+'|'+node.area+'|'+node.university_type})
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

UNIVERSITY_LIST = [] # 学校库的字典

SCHOOL_TRIE = SchoolTree() # 学校库的前缀树

def search_school(keyword, major=None, province=None):
    print('enter func . . . ')
    print('type before: %s' % type(province))
    print('province before: %s' % province)
    print('keyword before: %s' % keyword)

    #如果keyword是bytes, 则转化为str
    keyword = convert_to_str(keyword)
    province = convert_to_str(province)
    print('type after: %s' % type(province))
    print('keyword : %s ' % keyword)
    print('province : %s ' % province)
    global SCHOOL_TRIE
    print('func: '+str(id(SCHOOL_TRIE)))
    try:
        search_result = SCHOOL_TRIE.search(SCHOOL_TRIE.root, keyword)
    except:
        logging.error('没有正常返回结果')
        return exit_error_func(3, u'参数:'+keyword)

    result = []
    if len(search_result) > 0:
        status = 'success' #返回状态

        for each in search_result:
            if each['area'] == province:
                result.insert(0, each['result'])
            else:
                result.append(each['result'])
        if len(result) > 10:
            result = result[:10]
    else:
        status = 'success'

    print('result:%s' % result)
    return{
        'status': status,
        'result': result,
    }

def __init__(dict_from=None):
    start_time = time.time()
    _logging_conf()
    # 学校库来自配置的文本文件
    if dict_from == 'conf':
        try:
            for each in open('resource/university_dict.txt', 'r', encoding='utf-8').readlines():
                try:
                    each = each.strip('\r').strip('\n')
                    UNIVERSITY_LIST.append(each)
                except:
                    logging.error('some line is wrong when convent to dict .')
                    logging.info('wrong line : %s ', each)
                    return
        except FileNotFoundError:
            logging.error('File resource/university_dict.txt not found . . . ')

    # 学校库来自mongodb库
    elif dict_from == 'mongodb':

        try:
            for each in open('resource/db.conf', 'r', encoding='utf-8').readlines():
                try:
                    each = each.strip('\r').strip('\n')
                    if(each.split('=')[0] == 'mongodb.url'):
                        url = each.split('=')[1]
                    if(each.split('=')[0] == 'mongodb.port'):
                        port = each.split('=')[1]
                    if(each.split('=')[0] == 'mongodb.dulishuo.username'):
                        username = each.split('=')[1]
                    if(each.split('=')[0] == 'mongodb.dulishuo.password'):
                        password = each.split('=')[1]
                except:
                    logging.error('some line is wrong when read .')
                    logging.info('wrong line : %s ', each)
                    return
        except FileNotFoundError:
            logging.error('File resource/db.conf not found . . . ')
            return exit_error_func(3)

        mongo_client = MongoDB(url, port, username, password)
        school_search_collection = mongo_client.get_collection('search_school', 'dulishuo')
        for each in school_search_collection.find():
            UNIVERSITY_LIST.append(each['display_name']+'|'+each['origin_name']+'|'+each['area']+'|'+each['type']+'|'+str(each['ref_counter']))
    else:
        logging.error('__init__()出错，参数： %s' % dict_from)
        return exit_error_func(2, dict_from)

    # 构建学校库的前缀树
    global SCHOOL_TRIE
    SCHOOL_TRIE.setWords(UNIVERSITY_LIST)
    dict_tree_time = time.time()
    logging.info('院校库前缀树构建完毕，用时 %s 秒.' % str(dict_tree_time-start_time))

    writerr = open('gg.txt', 'w', encoding='utf-8')
    for each in SCHOOL_TRIE.preOrder(SCHOOL_TRIE.root):
        writerr.write(str(each))

def _logging_conf():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s [func:%(funcName)s] [line:%(lineno)d] %(levelname)s:\n%(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log/search_school.log',
                        filemode='a')
    logging.info('***********************************************')

if __name__ == '__main__':
    _logging_conf()
    __init__(dict_from='conf')
    keyword = 'zhongkeda'
    province = '北京'
    print(json.dumps(search_school(keyword=keyword, province=province), ensure_ascii=False, indent=4))

    #mon = MongoDB('123.57.250.189',27017,'dulishuo','Dulishuo123')
    #mon = MongoDB('123.57.250.189',27017)

    #dd = mon.get_collection('institute','dulishuo')
    #for each in dd.find():
        #print(str(type(each)))
    #mon =   MongoDB()d.next
    #print(mon.get_database('jianzhi'))
    #coll = mon.get_collection('test', 'test')
    #print(coll.find_one({'name': 'tim'}))