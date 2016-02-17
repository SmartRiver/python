#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'xiaohe'
__doc__     = '''this py is used to search schools related to the user input.
				Optional parameter includes area, which means the area user in.'''

import time
from common_func import exit_error_func
import logging
import sys
import json


class Trie(object):
    def __init__(self):
        self.root  = Node()  # Trie树root节点引用

    def add(self, word):
        ''' 添加字符串 '''
        university_type = word.split('|')[3]
        word_display = word.split('|')[1]
        word_search = word.split('|')[0]
        university_area = word.split('|')[2]
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
    def __init__(self, c=None, word=None, university_type=None, area=None):
        self.c          = c    # 节点存储的单个字符
        self.word       = word # 节点存储的用于展示的大学名
        self.university_type       = university_type # 节点存储的大学的类型
        self.area       = area # 节点存储的大学所在的地区（国内精确到省份，国外只精确国家）
        self.childs     = []   # 此节点的子节点kk

UNIVERSITY_LIST = []

TRIE = Trie()

def search_school(keyword, province=None):
    print('enter func . . . ')
    print('type before: %s' % type(province))

    #如果keyword是bytes。则转化为str
    keyword = convert_to_str(keyword)
    province = convert_to_str(province)
    print('type after: %s' % type(province))
    print('keyword : %s ' % keyword)
    print('province : %s ' % province)
    global TRIE
    print('func: '+str(id(TRIE)))
    try:
        search_result = TRIE.search(TRIE.root, keyword)
    except:
        logging.error('没有正常返回结果')
        exit_error_func(3, u'参数:'+keyword)

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
        status = 'fail'

    print('result:%s' % result)
    return{
        'status': status,
        'result': result,
    }

def __init__():
    _logging_conf()
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

    global TRIE
    TRIE.setWords(UNIVERSITY_LIST)

def _logging_conf():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s [func:%(funcName)s] [line:%(lineno)d] %(levelname)s:\n%(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log/search_school.log',
                        filemode='a')
    logging.info('***********************************************')

if __name__ == '__main__':
    _logging_conf()
    __init__()
    keyword = '华'
    province = '湖北'
    print(json.dumps(search_school(keyword, province), ensure_ascii=False, indent=4))
