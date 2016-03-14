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
import os
import assess_student
from assess_student import assess, init
import path_planning
from path_planning import schedule, init
import search
from search import search_school, init
from common_func import md5_token, convert_to_str, exit_error_func, process_param_string, return_json_dump
from global_variable import service_logger

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use python service for dulishuo.''')

class MainHandler(tornado.web.RequestHandler):

    def get(self, request_type):
        service_logger.info('request uri: %s' % urllib.parse.unquote(self.request.uri))
        service_logger.info('request IP: %s' % self.request.remote_ip)

        self.set_header('Access-Control-Allow-Origin','*')
        flag = True
        error_msg = ''
        # token验证
        if 'token' in self.request.query_arguments:
            token_requset = convert_to_str(self.request.query_arguments['token'][0])
            service_logger.info('request token :%s' % token_requset)
            token_server = md5_token(token_requset)
            if not token_server: # 发送的token跟服务器生成的token不一致
                service_logger.info('invalid token')
                self.finish(json.dumps(exit_error_func(4, 'token验证失败'), ensure_ascii=False, indent=4))

        if request_type == 'reload':
            try:
                if 'search_flag' in self.request.query_arguments:
                    search_flag = self.request.query_arguments['search_flag'][0]
                    search.init(convert_to_str(search_flag))
                    assess_student.init()
                    path_planning.init()
                else:
                    _init()
                service_logger.info('service reload success.')
                self.finish('reloaded.')
            except:
                service_logger.info('service reload success.')
                self.finish('failed.')
        elif request_type == 'school_search':
            print(str(type(self.request)))
            print(str(type(self.request.query_arguments)))
            for each in self.request.query_arguments:
                print('%s\t%s' % (each, convert_to_str(self.request.query_arguments[each][0])))
            try:
                param = fetch_params(self.request.query_arguments)

            except Exception as e:
                self.finish(return_json_dump(e))
            if 'condition' in self.request.query_arguments:
                condition = process_param_string(self.request.query_arguments['condition'][0])
            else:
                self.finish(return_json_dump(exit_error_func(5, 'condition是必选参数')))
            if 'area' in self.request.query_arguments:
                area = process_param_string(self.request.query_arguments['area'][0], option_param=1)
            else:
                area = None
            if 'country' in self.request.query_arguments:
                country = process_param_string(self.request.query_arguments['country'][0], option_param=1)
            else:
                country = None
            if 'major' in self.request.query_arguments:
                major = process_param_string(self.request.query_arguments['major'][0], option_param=1)
            else:
                major = None
            self.finish(json.dumps(search.search_school(condition=condition, major=major, area=area, country=country), ensure_ascii=False, indent=4))
        elif request_type == 'assess_student':
            if 'condition' in self.request.query_arguments:
                try:
                    condition = json.loads(convert_to_str(self.request.query_arguments['condition'][0]))
                except Exception as e:
                    service_logger.error(e)
                    error_msg = exit_error_func(1, 'condition格式转换出错')
                    flag = False
            else:
                error_msg = exit_error_func(5, 'condition为必选参数')
                flag = False
            if flag:
                assess_student.init()
                self.finish(json.dumps(assess_student.assess(condition), ensure_ascii=False, indent=4))
            else:
                self.finish(error_msg)
        elif request_type == 'path_planning':
            if 'condition' in self.request.query_arguments:
                try:
                    condition = json.loads(convert_to_str(self.request.query_arguments['condition'][0]))
                except Exception as e:
                    service_logger.error(e)
                    error_msg = exit_error_func(1, 'condition格式转换出错')
                    flag = False
            else:
                error_msg = exit_error_func(5, 'condition为必选参数')
                flag = False
            if 'size' in self.request.query_arguments:
                size = self.request.query_arguments['size'][0]
            else:
                size = None
            if flag:
                self.finish(json.dumps(path_planning.schedule(condition=condition, size=size), ensure_ascii=False, indent=4))
            else:
                self.finish(error_msg)
        else:
            service_logger.info('invalid request method.')
            self.finish(exit_error_func(7, request_type))

application = tornado.web.Application([(r"/(.*)", MainHandler)])

def _init():
    ''' 需要调用的模块统一初始化 '''
    search.init()
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
        service_logger.info('data_service server starts success.')
    except Exception as e:
        service_logger.error(e);
        service_logger.error('data_service server starts failed.')
