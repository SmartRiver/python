# -*- coding: utf-8 -*-
__author__ = 'Elliot'

import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
import sys
import json
from quest_process import quest2quest_dict
from match import find_nearest_offer, find_program, fill_score
import quest_process
import match
import select_school
import schedule
import os
from select_school import assess_applier
from django.utils.encoding import smart_str, smart_unicode


# Print the usage of the class
def print_usage():
    sys.stdout.write('''Welcome to use python service for dulishuo.

get:
    /question_process/(question_json)
        accept a list of question text
    /reload
        reload all dicts

Author:elliot.z
                     ''')


class MainHandler(tornado.web.RequestHandler):
    def get(self, request_type):
        if request_type == 'reload':
            try:
                quest_process.__init__()
                match.__init__()
                select_school.__init__()
                self.write('reloaded.')
            except:
                self.write('failed.')
        elif request_type == 'question_process':
            try:
                quest = smart_unicode(smart_str(self.request.query_arguments['q'][0]))
                result = quest2quest_dict(quest)
            except:
                raise MissingArgumentError('Invalid comment!')
            self.write(json.dumps(result, ensure_ascii=False, indent=4))
        elif request_type == 'find_nearest_offer':
            to_cmp = json.loads(self.request.query_arguments['condition'][0])
            fill_score(to_cmp)
            if 'num' in self.request.query_arguments:
                num = int(self.request.query_arguments['num'][0])
            else:
                num = 5
            offer_id_list = map(
                lambda x: int(x[1]['id']['$numberLong']),
                find_nearest_offer(to_cmp, num)
            )
            self.write(json.dumps(offer_id_list, ensure_ascii=False, indent=4))
        elif request_type == 'find_school':
            to_cmp = json.loads(self.request.query_arguments['condition'][0])
            fill_score(to_cmp)
            if 'num' in self.request.query_arguments:
                num = int(self.request.query_arguments['num'][0])
            else:
                num = 5
            self.write(json.dumps(find_program(to_cmp, num), ensure_ascii=False, indent=4))
        elif request_type == 'assess_applier':
            to_assess = json.loads(self.request.query_arguments['condition'][0])

            self.set_header('Access-Control-Allow-Origin','*')
            self.write(json.dumps(assess_applier(to_assess), ensure_ascii=False, indent=4))
        elif request_type == 'study_schedule':
            to_schedule = json.loads(self.request.query_arguments['condition'][0])

            self.set_header('Access-Control-Allow-Origin','*')
            self.write(json.dumps(schedule(to_schedule), ensure_ascii=False, indent=4))
        else:
            raise MissingArgumentError('Invalid command!')

settings = {"static_path": os.path.join(os.path.dirname(__file__), "resource")}
application = tornado.web.Application([
    (r"/(.*)", MainHandler),
    (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
