#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author_ = 'johnosn'
__doc__   = '''this file is select several appropriate universities for school'''

import configparser
from db_util import MySqlDB

def get_avg_score_by_program(major_id):
    '''根据major_id返回关联申请成功的案例offer的平均成绩'''
    # 读取mysql数据库连接参数配置文件
    cf = configparser.ConfigParser()
    cf.read('conf/db.conf')
    s = cf.sections()
    host     = cf.get('mysql_hechuang', 'host')
    port     = cf.getint('mysql_hechuang', 'port')
    user     = cf.get('mysql_hechuang', 'user')
    password = cf.get('mysql_hechuang', 'password')

    # 获取该专业的所有的offer成绩
    my_sql = MySqlDB(host, port, user, password, 'hechuang')
    my_cursor = my_sql.get_cursor()
    sql = 'select * from offer_result where major_id = %s and result = %s'
    my_cursor.execute(sql, (major_id, '成功'))
    result = my_cursor.fetchall()

    for each in result:
        print(each['id'])

if __name__ == '__main__':
    get_avg_score_by_program(8)