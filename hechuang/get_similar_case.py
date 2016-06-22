#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__doc__     = '''this file defined some methods used to match similar cases for student.'''

from common_func import (exit_error_func, convert_gre_to_gmat, convert_gre_to_gmat)

class offerNode(object):
    '''将每个offer案例当作树的一个节点'''
    def __init__(self, id=None, gpa=None, institute=None, institute_type=None, toefl=None, gre=None, gmat=None):
        self.id     = id # 节点存储的offer的id
        self.gpa    = gpa # 节点存储offer的gpa的分数
        self.institute  = institute # 节点存储offer的学校id
        self.institute_type = institute_type # 节点存储的offer的学校类型
        self.toefl  = toefl # 节点存储的offer的toefl总分
        self.gre    = gre # 节点存储的offer的gre总分
        self.gmat   = gmat # 节点存储的offer的gmat总分

class offerTree(object):
    '''offer树'''
    def __init(self):
        self.root = offerNode()
    
    def add(self, offer):
        '''添加offer节点'
        pass

def get_similar():
    pass
        
