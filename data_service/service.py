#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__doc__     = '''this file is used to process all of requests from clients'''

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
import sys
import json
import urllib.parse
from tornado.escape import url_escape, url_unescape, json_encode, json_decode
import os
import assess_student
from assess_student import assess, init
import path_planning
from path_planning import schedule, init
import search
from search import search_school, init
from common_func import exit_error_func, return_json_dump, fetch_params, client_token_check, convert_var_type
from global_variable import service_logger, error_logger, INTERFACE_METHOD

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use data interface service for dulishuo.''')

REQUEST_METHOD = { # 方法请求对应的处理模块函数名
    'school_search': 'search.search_school', # 学校联想搜索算法
    'assess_student': 'assess_student.assess', # 学生条件评估算法
    'path_planning': 'path_planning.schedule', # 路径规划算法
}

class MainHandler(tornado.web.RequestHandler):

    def get(self, request_type):
        service_logger.info('request uri: %s' % convert_var_type(urllib.parse.unquote(self.request.uri), 'string'))
        service_logger.info('request IP: %s' % self.request.remote_ip)
        self.set_header('Access-Control-Allow-Origin','*')
        
        if request_type not in INTERFACE_METHOD:
            return self.finish(exit_error_func(7, request_type))
        if request_type == 'reload':
            try:
                if 'search_flag' in self.request.query_arguments:
                    search_flag = convert_var_type(self.request.query_arguments['search_flag'][0], 'string')
                    _init(search_flag=search_flag)
                else:
                    _init()
                service_logger.info('service reload success.')
                return self.finish('reload success')
            except:
                error_logger.error('service reload failed.')
                return self.finish('reload failed')
        try:
            if 'token' in self.request.query_arguments: # token验证
                if client_token_check(self.request.query_arguments['token'][0]) == False:
                    return self.finish(exit_error_func(4))
            param = INTERFACE_METHOD[request_type] # 获取请求方法对应的参数列表
            print('param'+str(param))
            param = fetch_params(self.request.query_arguments, *param)
            print('param'+str(param))
            exec('self.finish(return_json_dump('+REQUEST_METHOD[request_type]+'(**param)))')
            return
        except Exception as e:
            error_logger.error('Exception:'+str(e))
            return self.finish((exit_error_func(1, str(e))))


application = tornado.web.Application([(r"/(.*)", MainHandler)])

def _init(search_flag='mongodb'):
    ''' 需要调用的模块统一初始化 '''
    #search.init(dict_from=search_flag)
    service_logger.info('[success] init search')
    assess_student.init()
    service_logger.info('[success] init assess_student')
    path_planning.init()
    service_logger.info('[success] init path_planning')

if __name__ == "__main__":
    try:
        service_logger.info('data_service server starting.')
        _init() # 将需要引用的模块统一初始化
        application.listen(8826)
        tornado.ioloop.IOLoop.instance().start()
        service_logger.info('data_service server starts success.\n')
    except Exception as e:
        error_logger.error(e);
        error_logger.error('data_service server starts failed.\n')
