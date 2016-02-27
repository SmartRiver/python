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
    "major":"cs",
    "grade":"1",
    "target":"1",
    "data":{
        "gpa":{"score":"3.2", "trend":"2", "school":"华中科技大学|湖北|985"},
        "gmat":{"total":"300", "writing":"3", "verbal":"12", "maths":"12"},
        "gre":{"total":"300", "writing":"4", "verbal":"12", "maths":"12"},
        "toefl":{"total":"110", "writing":"3", "reading":"12", "listening":"12", "speaking":"12"},
        "ielts":{"total":"7", "writing":"3", "reading":"12","listening":"12", "speaking":"12"},
        "research":{"duration":"1", "level":"1", "achievement":"1", "recommendation":"1"},
        "work":{"duration":"1", "level":"1", "recommendation":"1"},
        "internship":{"duration":"5", "level":"3", "recommendation":"2"},
        "activity":{"duration":"1", "type":"1"},
        "credential":{"level":"2"},
        "competition":{"level":"2"},
        "scholarship":{"level":"2"}
    }
}

#assess_student.init()
#path_planning.init()
#print(json.dumps(path_planning.schedule(student_info), ensure_ascii=False, indent=4))
#print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))

#tt = db_util.get_connection()
#print(tt)

if __name__ == '__main__':
    key_b = 7
    key_a = 1237
    key = 'dulishuo'

    now = time.gmtime() # 获取当前UTC统一时间，与时区无关
    year = now.tm_year
    month = now.tm_mon
    day = now.tm_mday
    hour = now.tm_hour
    print('-%d-%d-%d-%d-' % (year, month, day, hour))
    y = year % key_b
    m = month % key_b
    d = day % key_b
    h = hour % key_b
    tt = ''.join(str(x * key_a) for x in [y, m, d, h])
    print('---%s----' % tt)
    key = ''.join(str(ord(x)) for x in key)
   
    print('-%d-%d-%d-%d-' % (y, m, d, h))
    md = hashlib.md5()
    md.update((tt+key).encode('utf-8'))
    token = md.hexdigest()[:16]
    
    token = list(token)
   
    token[3] = str(y)
    token[7] = str(m)
    token[11] = str(d)
    token[15] = str(h)
    print('-----%s-' % token)
    print(md5_token(''.join(token)))