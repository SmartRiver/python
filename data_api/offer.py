#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__doc__     = '''functions in this file are used to process all of data requests related to offer. '''

from global_variable import OFFER

def getOfferByMajor(mid, size=5, group=0):
    '''获取指定专业的Offer,如果group为1,则结果按学校分组'''
    pass

def getOfferByInstitute(sid, size=5, group=0):
    '''获取指定学校的Offer,如果group为1,则结果按专业分组'''
    pass

def getOfferByInstituteAndMajor(sid, mid, size=10):
    '''获取指定学校和专业的Offer,默认返回不大于10个结果'''
    pass