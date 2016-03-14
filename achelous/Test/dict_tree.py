#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Trie树实现字符串数组字典排序'''
import sys
import imp
import time


class Trie(object):
    def __init__(self):
        self.root  = Node() # Trie树root节点引用

    def add(self, word):
        '''添加字符串'''
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
        search_result = []
        _len = len(word)
        temp_root = None
        global TREE_DEEP
        for level in range(1, TREE_DEEP):
            #print('deep: %d ' % level)

            if level > 5:
                return search_result
            for each_node in node.childs:
                if each_node.c == word[0]:
                    if _len == 1:
                        return self.preOrder(each_node)
                    else:
                        search_result.extend(self.search(each_node, word[1:]))
            if len(search_result) > 0:
                return search_result
            else:

                # for xxoo in node.childs:
                #     search_result.extend(self.search(xxoo, word))



class Node(object):
    def __init__(self, c=None, word=None):
        self.c = c    # 节点存储的单个字符
        self.word = word  # 节点存储的词
        self.childs = []   # 此节点的子节点
LLL = []
flag = 1
TREE_DEEP = 1

UNIVERSITY_SET = set()

def __init__():
    for each in open('university_dict.txt', 'r', encoding='utf-8').readlines():
        each = each.strip('\r').strip('\n')
        UNIVERSITY_SET.add(each)
        global TREE_DEEP
        if len(each) > TREE_DEEP:
            TREE_DEEP = len(each)

if __name__ == '__main__':
    start_time = time.time()

    print(sys.getdefaultencoding())
    __init__()
    print()
    trie = Trie()

    trie.setWords(UNIVERSITY_SET)
    #print(trie.preOrder(trie.root))
    # print('原始字符串数组:     %s' % words)
    test_set = ('北京工', '上海交', '外国语')
    for each in test_set:
        result = trie.search(trie.root, each)
   # print('len : %d' % len(result))
        print(result)
    end_time = time.time()
    print('use time : %d' % (end_time-start_time))
