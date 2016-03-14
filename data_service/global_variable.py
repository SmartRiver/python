#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  = 'johnson'
__doc__     = '''this file is used to manage global variables'''

import logging
import logging.config

def _logging_conf():
    '''日志配置'''
    try:
        logging.config.fileConfig('./conf/logging.conf')
        service_logger = logging.getLogger('general')
        service_logger.info('--------logging configurating success--------')
        return service_logger
    except Exception as e:
        print('--------logging configurating failed--------')

service_logger = _logging_conf()