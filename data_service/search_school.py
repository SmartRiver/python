#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'xiaohe'
__doc__     = '''this py is used to search schools related to the user input.
				Optional parameter includes area, which means the area user in.'''


import time
#from common_func import exit_error_func
import logging
import sys


class Trie(object):
    def __init__(self):
        self.root  = Node() # Trie树root节点引用

    def add(self, word):
        ''' 添加字符串 '''
        node = self.root
        for c in word:
            pos = self.find(node, c)
            if pos < 0:
                node.childs.append(Node(c))
                #为了图简单，这里直接使用Python内置的sorted来排序
                #pos有问题，因为sort之后的pos会变掉,所以需要再次find来获取真实的pos
                #自定义单字符数组的排序方式可以实现任意规则的字符串数组的排序
                node.childs = sorted(node.childs, key=lambda child: child.c)
                pos = self.find(node, c)
            node = node.childs[pos]
        node.word = word

    def preOrder(self, node):
        '''先序输出'''
        results = []
        if node.word:
            results.append(node.word)
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
    def __init__(self, c=None, word=None):
        self.c          = c    # 节点存储的单个字符
        self.word       = word # 节点存储的词
        self.childs     = []   # 此节点的子节点

UNIVERSITY_TYPE_DICT = {}
UNIVERSITY_ALIAS_DICT = {}

trie = Trie()

def search_school(self, keyword, province='null'):
    print('enter func . . . ')
    global trie
    result = trie.search(keyword)
    print('result:'+result)
    return{
        'status': 'success',
        'result': result,
    }

def __init__():
    try:
        for each in open('resource/university_dict.txt', 'r', encoding='utf-8').readlines():
            try:
                each = each.strip('\r').strip('\n')
                UNIVERSITY_TYPE_DICT[each.split('|')[0]] = each.split('|')[3]
                UNIVERSITY_ALIAS_DICT[each.split('|')[0]] = each.split('|')[1]
            except:
                logging.error('some line is wrong when convent to dict .')
                logging.info('wrong line : %s ', each)
                return
    except FileNotFoundError:
        logging.error('File resource/university_dict.txt not found . . . ')

    global trie
    trie.setWords(UNIVERSITY_TYPE_DICT.keys())

def logging_conf():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s [func:%(funcName)s] [line:%(lineno)d] %(levelname)s:\n%(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log/search_school.log',
                        filemode='a')
    logging.info('***********************************************')
