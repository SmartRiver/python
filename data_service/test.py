import json
import assess_student
from assess_student import assess, init
import path_planning
from path_planning import schedule, init
import db_util
from db_util import get_connection
from common_func import md5_token, return_json_dump
import search
from search import search_school, init
import hashlib
import time

import json
import logging

student_info = {"major":"cs","grade":1,"target":"1","data":{"gpa":{"score":"3.5","school":"北京北大方正软件职业技术学院|北京|双非二本"},"gmat":{"total":"0","writing":"0"},"gre":{"total":"328","writing":"4","verbal":"0"},"toefl":{"total":"106","speaking":"25"},"ielts":{"total":"0"},"research":{"duration":"5","level":"2","achievement":"2","recommendation":"2"},"work":{"duration":"","level":"","recommendation":""},"internship":{"duration":"2","level":"2","recommendation":"1"},"activity":{"duration":"1","type":"2"},"competition":{"level":"2"},"scholarship":{"level":"2"},"credential":{"level":"2"}}}

tt = {'condition': '交通', 'area': 'xx', 'country': None}
assess_student.init()
path_planning.init()
#search.init();
#print(return_json_dump(search.search_school(**tt)))
path_planning.schedule(student_info, size=1)
#print(json.dumps(path_planning.schedule(student_info, size=1), ensure_ascii=False, indent=4))
#print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))
#search.init()
#print(json.dumps(search.search_school(condition='a', country=None), ensure_ascii=False, indent=4))