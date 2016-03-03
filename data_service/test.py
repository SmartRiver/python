import json
import assess_student
from assess_student import assess, init
import path_planning
from path_planning import schedule, init
import db_util
from db_util import get_connection
from common_func import md5_token
import search
from search import search_school, init
import hashlib
import time

import json
import logging

student_info = {"major":"xx","grade":"1","target":"1","data":{"gpa":{"score":"", "trend":"", "school":""},"gmat":{"total":"", "writing":"", "verbal":"", "maths":""},"gre":{"total":"", "writing":"", "verbal":"", "maths":""},"toefl":{"total":"", "writing":"", "reading":"", "listening":"", "speaking":""},"ielts":{"total":"", "writing":"", "reading":"","listening":"", "speaking":""},"research":{"duration":"1", "level":"1", "achievement":"1", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"1", "level":"1", "recommendation":"1"},"reletter":{"level":["1","2","3"]},"activity":{"duration":"1", "type":"1"},"credential":{"level":"2"},"competition":{"level":"2"},"scholarship":{"level":"2"}}}


assess_student.init()
path_planning.init()
#print(json.dumps(path_planning.schedule(student_info, size=1), ensure_ascii=False, indent=4))
print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))
#search.init()
#print(json.dumps(search.search_school(condition='a', country=None), ensure_ascii=False, indent=4))