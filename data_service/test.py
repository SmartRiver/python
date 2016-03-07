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

student_info = {'target': '2', 'data': {'internship': {'level': '4', 'recommendation': '3', 'duration': '5'}, 'ielts': {'total': '0'}, 'toefl': {'total': '0', 'speaking': '0'}, 'gpa': {'score': '3.3', 'school': '12'}, 'research': {'level': '6', 'recommendation': '3', 'achievement': '5', 'duration': '5'}, 'scholarship': {'level': '7'}, 'activity': {'duration': '3', 'type': '2'}}, 'grade': 1, 'major': 'law'}
assess_student.init()
path_planning.init()
#path_planning.schedule(student_info, size=1)



#print(json.dumps(path_planning.schedule(student_info, size=1), ensure_ascii=False, indent=4))
print(json.dumps(assess_student.assess(student_info), ensure_ascii=False, indent=4))
#search.init()
#print(json.dumps(search.search_school(condition='a', country=None), ensure_ascii=False, indent=4))
# 周一：完善学校搜索算法和接口的工作，重构接口代码；
# 周二：开始路径规划算法的工作，扩充学校联想搜索的词库；
# 周三：完成路径规划算法和接口的工作，重构接口代码；
# 周四：调节路径规划的的算法和学习网络传输协议相关的知识；
# 周五：添加学生软硬实力分析算法和接口返回，协同处理产品bug；
# 周六：将人工补充的申请方的offer数据处理入库，协同处理产品bug；
