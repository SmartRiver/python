#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__  = 'johnson'
__doc__     = '''this file is used to process all of requests from clients'''

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError, gen
import sys
import json
import pymongo
from pymongo import MongoClient
import time
from time import sleep
import urllib.parse
import tornado.escape
from tornado.escape import url_escape, url_unescape, json_encode, json_decode
import os
from common_func import exit_error_func, return_json_dump, fetch_params, client_token_check, convert_var_type
import global_variable_initialization
from global_variable import service_logger, error_logger, INTERFACE_METHOD

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use data interface service for dulishuo.''')

REQUEST_METHOD = { # 方法请求对应的处理模块函数名
    'school_search': 'search.search_school', # 学校联想搜索算法
    'assess_student': 'assess_student.assess', # 学生条件评估算法
    'path_planning': 'path_planning.schedule', # 路径规划算法
}

class MongoDB():
    def __init__(self, host, port, database, collection, username=None, password=None):
        #初始化类成员变量
        self.host = host
        self.port = port
        self.database = database
        self.collection = collection
        self.username = username
        self.password = password
        
        self._client_ = MongoClient(self.host, self.port)
        #print('数据库连接已创建')
        
        self._db_ = self._client_[self.database]
        if not self.username == None and not self.password == None:
            if self._db_.authenticate(self.username, self.password, mechanism='SCRAM-SHA-1'):
                print('数据库授权成功')
            else:
                print('数据库授权失败')
                
        self._collection_ = self._db_[self.collection]
       
#    def __del__(self):
#        if not self._client_ == None:
#            self._client_.close()
#            print('数据库连接已关闭')
            
    def get_collection(self):
        return self._collection_

def _connect_db():
    try:
        mongodb = MongoDB('101.201.209.208',20000,'test','collection')
        collection = mongodb.get_collection()   
        res = collection.find_one()

        return res['name']
    except Exception as err:
        print(err)

def xxxx():
    print('xxx')

def cor_test():
    resp = _connect_db()
    return resp

class TestHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    async def post(self, request_method):
        try:
            #print('request uri: %s' % convert_var_type(urllib.parse.unquote(self.request.uri), 'string'))
            #print('request IP: %s' % self.request.remote_ip)
            self.set_header('Access-Control-Allow-Origin','*')
        
            print('enter . . . :'+self.get_argument('name'))
            xxx = await cor_test()
            #xxx = _connect_db()
            xx = str(self.request.request_time())
            print('after with : '+ str(xxx))
            print('use time : '+xx)
            self.write(xx)
            print('end')
            self.finish()
        except Exception as e:
            print(e)

    @tornado.web.asynchronous    
    def get(self, request_method):
        #print('request uri: %s' % convert_var_type(urllib.parse.unquote(self.request.uri), 'string'))
        #print('request IP: %s' % self.request.remote_ip)
        self.set_header('Access-Control-Allow-Origin','*')

        print('get')
        print('request_method: %s' % request_method)
        xx = str(self.request.request_time())
        self.write('use time : '+xx)
        self.finish()
        signature = self.get_argument('signature').decode('utf-8')
        timestamp = self.get_argument('timestamp').decode('utf-8')
        nonce = self.get_argument('nonce').decode('utf-8')
        token = 'achelous0306'
        tmp_list = list(timestamp, nonce, token)
        tmpp_list = sorted(tmp_list)
        tmp_str = ''.join(tmpp_list)
        sha = hashlib.sha1()
        sha.update(tmp_str)
        s = sha.hexdigest()
        print(s)
        if s == signature:
            print(True)



class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self, request_type):
        
        try:
            
            service_logger.info('request uri: %s' % convert_var_type(urllib.parse.unquote(self.request.host+self.request.uri), 'string'))
            service_logger.info('request IP: %s' % self.request.remote_ip)
            self.set_header('Access-Control-Allow-Origin','*')
            if 'token' in self.request.query_arguments: # token验证
                if client_token_check(self.request.query_arguments['token'][0]) == False:
                    return self.finish(exit_error_func(4))
            print(str(self.request.arguments))
            for each in self.request.arguments:
                print(str(each)+'\t'+self.request.arguments[each][0].decode('utf-8')+'\t'+str(type(self.request.arguments[each][0].decode('utf-8'))))
            if 'method' not in self.request.arguments:
                print('haha')
            print('method:'+request_type)
            # param = INTERFACE_METHOD[request_type] # 获取请求方法对应的参数列表
            # print('param'+str(param))
            # param = fetch_params(self.request.query_arguments, *param)
            # print('param'+str(param))
            # exec('self.finish(return_json_dump('+REQUEST_METHOD[request_type]+'(**param)))')
            self.finish(return_json_dump({'code':200,'message':'success'}))
            return
        except Exception as e:
            print(e)
            #error_logger.error('Exception:'+str(e))
            return self.finish((exit_error_func(1, str(e))))

settings = {
        'debug': True, # 开发模式
        'gzip': True, # 支持gzip压缩
        'autoescape': None,
        'xsrf_cookies': False,
    }

application = tornado.web.Application([
    (r"/v1/(.*)", MainHandler),
    (r"/test/(.*)", TestHandler),
    ], **settings)

def _init(search_flag='mongodb'):
    ''' 需要调用的模块统一初始化 '''
    pass

if __name__ == "__main__":
    try:
        #print('data_service server starting.')
        #_init() # 将需要引用的模块统一初始化
        application.listen(8836)
        tornado.ioloop.IOLoop.instance().start()
        #print('data_service server starts success.\n')
    except Exception as e:
        pass
        #error_logger.error(e);
        #error_logger.error('data_service server starts failed.\n')
