# -*- coding: utf-8 -*-
__author__ = 'xiaohe'

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
import sys
import json
import os
import search_school
from search_school import search_school

# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use python service for dulishuo.''')



class MainHandler(tornado.web.RequestHandler):

    def get(self, request_type):
        if request_type == 'reload':
            try:
                search_school.__init__();
                self.write('reloaded.')
            except:
                self.write('failed.')
        elif request_type == 'school_search':
            keyword = self.request.query_arguments['condition'][0]
            self.set_header('Access-Control-Allow-Origin','*')
            if 'province' in self.request.query_arguments:
                province = self.request.query_arguments['province'][0]
                self.write(json.dumps(search_school(keyword, province), ensure_ascii=False, indent=4))
            else:
                self.write(json.dumps(search_school(keyword), ensure_ascii=False, indent=4))




application = tornado.web.Application([(r"/.*)", MainHandler),])

if __name__ == "__main__":
    application.listen(8806)
    tornado.ioloop.IOLoop.instance().start()
