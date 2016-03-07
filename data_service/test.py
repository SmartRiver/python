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

 # student_info = {"major":"marketing","grade":"2","target":"哈佛大学","data":{"gpa":{"score":"3", "trend":"2", "school":"9"},"gre":{"total":"301","verbal":"160","writing":"5"},"toefl":{"total":"105", "writing":"", "reading":"", "listening":"", "speaking":"28"},"ielts":{"total":"6", "writing":"", "reading":"","listening":"", "speaking":""},"research":{"duration":"4", "level":"3", "achievement":"2", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"5", "level":"3", "recommendation":"1"},"reletter":{"level":["1","2","3"]},"activity":{"duration":"3", "type":"2"},"credential":{"level":"4"},"competition":{"level":"2"},"scholarship":{"level":"3"}}}
# student_info = {"major":"economics","grade":"2","target":"2","data":{"gpa":{"score":"3.2", "trend":"2", "school":"9"},"gre":{"total":"0","verbal":"0","writing":""},"toefl":{"total":"", "writing":"", "reading":"", "listening":"", "speaking":""},"ielts":{"total":"", "writing":"", "reading":"","listening":"", "speaking":""},"research":{"duration":"4", "level":"3", "achievement":"2", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"5", "level":"3", "recommendation":"1"},"reletter":{"level":["1","2","3"]},"activity":{"duration":"3", "type":"2"},"credential":{"level":"4"},"competition":{"level":"4"},"scholarship":{"level":"4"}}}

student_info = {"major":"cs","grade":"1","target":"xxx","data":{"gpa":{"score":"3.2", "trend":"2", "school":"华中科技大学|湖北|985"},"gmat":{"total":"0", "writing":"3", "verbal":"12", "maths":"12"},"gre":{"total":"0", "writing":"4", "verbal":"12", "maths":"12"},"toefl":{"total":"1", "writing":"3", "reading":"12", "listening":"12", "speaking":"12"},"ielts":{"total":"9", "writing":"3", "reading":"12","listening":"12", "speaking":"12"},"research":{"duration":"1", "level":"1", "achievement":"1", "recommendation":"1"},"work":{"duration":"1", "level":"1", "recommendation":"1"},"internship":{"duration":"1", "level":"1", "recommendation":"1"},"reletter":{"level":["1","2","3"]},"activity":{"duration":"1", "type":"1"},"credential":{"level":"2"},"competition":{"level":"2"},"scholarship":{"level":"2"}}}
assess_student.init()
path_planning.init()
path_planning.schedule(student_info, size=1)



print(json.dumps(path_planning.schedule(student_info, size=1), ensure_ascii=False, indent=4))
#print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))
#search.init()
#print(json.dumps(search.search_school(condition='a', country=None), ensure_ascii=False, indent=4))
# 周一：完善学校搜索算法和接口的工作，重构接口代码；
# 周二：开始路径规划算法的工作，扩充学校联想搜索的词库；
# 周三：完成路径规划算法和接口的工作，重构接口代码；
# 周四：调节路径规划的的算法和学习网络传输协议相关的知识；
# 周五：添加学生软硬实力分析算法和接口返回，协同处理产品bug；
# 周六：将人工补充的申请方的offer数据处理入库，协同处理产品bug；
