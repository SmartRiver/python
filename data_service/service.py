# -*- coding: utf-8 -*-
__author__ = 'johnson'

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
import sys
import json
import urllib.parse
import os
import logging
import logging.config
import search
from search import search_school
from common_func import md5_token, convert_to_str, exit_error_func

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use python service for dulishuo.''')

class MainHandler(tornado.web.RequestHandler):

    def get(self, request_type):
        service_logger.info('request uri: %s' % urllib.parse.unquote(self.request.uri))
        # token验证
        if 'token' in self.request.query_arguments:

            token_requset = convert_to_str(convert_to_str(self.request.query_arguments['token'][0]))
            service_logger.info('request token :%s' % token_requset)
            token_server = md5_token()
            if token_requset != token_server: # 发送的token跟服务器生成的token不一致
                self.write(json.dumps(exit_error_func(4), ensure_ascii=False, indent=4))

        if request_type == 'reload':
            #service_logger.info('请求uri:%s' % self.request.uri)
            try:
                if 'search_flag' in self.request.query_arguments:
                    search_flag = self.request.query_arguments['search_flag'][0]
                    search.__init__(convert_to_str(search_flag))
                else:
                    search.__init__()
                self.write('reloaded.')
            except:
                self.write('failed.')
        elif request_type == 'school_search':
            if 'condition' in self.request.query_arguments:
                condition = self.request.query_arguments['condition'][0]
            else:
                self.write(json.dumps(exit_error_func(5, '[conditon]')), ensure_ascii=False, indent=4)
            if 'area' in self.request.query_arguments:
                area = self.request.query_arguments['area'][0]
            else:
                area = None
            if 'major' in self.request.query_arguments:
                major = self.request.query_arguments['major'][0]
            else:
                major= None
            self.set_header('Access-Control-Allow-Origin','*')
            self.write(json.dumps(search_school(condition=condition, major=major, area=area), ensure_ascii=False, indent=4))
        else:
            raise MissingArgumentError('Invalid command!')

global service_logger # logger

'''日志配置'''
def __logging_conf():
    try:
        global service_logger
        logging.config.fileConfig('./conf/logging.conf')
        service_logger = logging.getLogger('general')
        service_logger.info('--------completing confuration--------')
    except Exception as e:
        print('--------logging configurating failed--------')

application = tornado.web.Application([(r"/(.*)", MainHandler)])


if __name__ == "__main__":
    __logging_conf()
    try:
        service_logger.info('data_service server starting.')
        application.listen(8826)
        tornado.ioloop.IOLoop.instance().start()
        service_logger.info('data_service server starts success.')
    except:
        service_logger.error('data_service server starts failed.')
