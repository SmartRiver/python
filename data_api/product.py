#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__doc__     = '''functions in this file are used to process all of data requests related to institute. '''

from global_variable import INSTITUTE

def getInstituteInfoById(sid):
    '''根据学校ID获取学校的基本信息'''
    return INSTITUTE[sid]
      