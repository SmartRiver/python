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

<<<<<<< HEAD
student_info = {"major":"materials","grade":"3","target":"2","data":{"gpa":{"score":"3.8", "school":"9"},"gre":{"total":"340","verbal":"170","writing":"0"},"gmat":{"total":"800","writing":"5"},"toefl":{"total":"120", "writing":"30", "reading":"", "listening":"", "speaking":"30"},"ielts":{"total":"9", "writing":"", "reading":"","listening":"", "speaking":"9"},"research":{"duration":"4", "level":"2", "achievement":"2", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"1", "level":"1", "recommendation":"1"},"activity":{"duration":"1", "type":"1"},"competition":{"level":"2"},"scholarship":{"level":"7"}}}
=======
student_info = {"major":"cs","grade":"3","target":"2","data":{"gpa":{"score":"3.5", "trend":"2", "school":"9"},"gre":{"total":"320","verbal":"160","writing":"5"},"toefl":{"total":"110", "writing":"", "reading":"", "listening":"", "speaking":""},"ielts":{"total":"6", "writing":"", "reading":"","listening":"", "speaking":""},"research":{"duration":"4", "level":"2", "achievement":"2", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"5", "level":"4", "recommendation":"1"},"reletter":{"level":["1","2","3"]},"activity":{"duration":"4", "type":"5"},"credential":{"level":"4"},"competition":{"level":"5"},"scholarship":{"level":"7"}}}
>>>>>>> 4ad9f633b362a5014bed63219e1697d44e122485


assess_student.init()
path_planning.init()
#path_planning.schedule(student_info, size=1)
print(json.dumps(path_planning.schedule(student_info, size=1), ensure_ascii=False, indent=4))
#print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))
#search.init()
#print(json.dumps(search.search_school(condition='a', country=None), ensure_ascii=False, indent=4))