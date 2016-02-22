# -*- coding: utf-8 -*-
__author__ = 'xiaohe'

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
import sys
import json
import os
import search
from search import search_school
from common_func import md5_token, convert_to_str, exit_error_func

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use python service for dulishuo.''')



class MainHandler(tornado.web.RequestHandler):

    def get(self, request_type):
        # token验证
        if 'token' in self.request.query_arguments:
            token_requset = convert_to_str(self.request.query_arguments['token'][0])
            token_server = md5_token()
            if token_requset != token_server: # 发送的token跟服务器生成的token不一致
                return exit_error_func(4)

        if request_type == 'reload':
            try:
                if 'search_flag' in self.request.query_arguments:
                    search.__init__(self.request.query_arguments['search_flag'][0].decode('utf-8'))
                else:
                    search.__init__()
                self.write('reloaded.')
            except:
                self.write('failed.')
        elif request_type == 'school_search':

            if 'condition' in self.request.query_arguments:
                keyword = self.request.query_arguments['condition'][0]
            else:
                raise MissingArgumentError('Invalid command!')
            if 'province' in self.request.query_arguments:
                province = self.request.query_arguments['province'][0]
            else:
                province = None
            if 'major' in self.request.query_arguments:
                major = self.request.query_arguments['major'][0]
            else:
                major= None
            self.set_header('Access-Control-Allow-Origin','*')
            self.write(json.dumps(search_school(keyword=keyword, major=major, province=province), ensure_ascii=False, indent=4))
        else:
            raise MissingArgumentError('Invalid command!')




application = tornado.web.Application([(r"/(.*)", MainHandler)])

if __name__ == "__main__":
    application.listen(8826)
    tornado.ioloop.IOLoop.instance().start()
