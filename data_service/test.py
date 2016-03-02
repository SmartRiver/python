import json
import assess_student
from assess_student import assess, init
import path_planning
from path_planning import schedule, init
import db_util
from db_util import get_connection
from common_func import md5_token
import hashlib
import time

import json
import logging

student_info = {
    "major":"mathematics",
    "grade":"3",
    "target":"1",
    "data":{
        "gpa":{"score":"3", "trend":"2", "school":"ggg|usa|985"},
        "gmat":{"total":"300", "writing":"3", "verbal":"12", "maths":"12"},
        "gre":{"total":"200", "writing":"4", "verbal":"12", "maths":"12"},
        "toefl":{"total":"1", "writing":"0", "reading":"12", "listening":"12", "speaking":"1"},
        "ielts":{"total":"0", "writing":"0", "reading":"12","listening":"12", "speaking":"0"},
        "research":{"duration":"1", "level":"1", "achievement":"1", "recommendation":"1"},
        "work":{"duration":"1", "level":"1", "recommendation":"1"},
        "internship":{"duration":"5", "level":"3", "recommendation":"2"},
        "activity":{"duration":"1", "type":"1"},
        "competition":{"level":"2"},
        "scholarship":{"level":"2"}
    }
}


assess_student.init()
path_planning.init()
print(json.dumps(path_planning.schedule(student_info), ensure_ascii=False, indent=4))
#print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))


