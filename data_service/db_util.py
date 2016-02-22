# -*- coding: utf:-8 -*-

import pymongo
from pymongo import MongoClient

__author__ = 'xiaohe'
__doc__ = '''this py file is the collection of those operation functions or methods used in db'''

class MongoDB():
    def __init__(self, host, port, username='null', password='null'):
        #初始化类成员变量
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        #建立连接
        self._client_ = MongoClient(self.host, self.port)
        
    def get_database(self, db_name):
        self._db_name = self._client_[db_name]

        try:
            if self._db_name.authenticate(self.username, self.password, mechanism='SCRAM-SHA-1'):
                print('验证成功')
                return self._db_name
            else:
                print('用户名/密码/验证方式错误')
                return False
        except:
            return False


    def get_collection(self, collection_name, db_name=None):
        if not db_name == None:
            if self.get_database(db_name) == False:
                return False
            else:
                self._db_name = self.get_database(db_name)
        return self._db_name[collection_name]
    
    def find_one(self):
        return self._collection_.find_one()
        
    def insert_one(self, document):
        return self._collection_.insert_one(document).inserted_id
    def close(self):
        self._client_.close()

if __name__ == '__main__':
    # _logging_conf()
    # __init__()
    # keyword = 'h'
    # province = 'USA'
    # print(json.dumps(search_school(keyword, province), ensure_ascii=False, indent=4))

    mon = MongoDB('123.57.250.189',27017,'gfulishuo','Dulishuo123')
    #mon = MongoDB('123.57.250.189',27017)
    dd = mon.get_collection('institute','dulishuo')
    if dd == False:
        print(dd)
        exit(-1)
    print(dd.find_one({'ttitle':'哈佛大学'}))
    #mon =   MongoDB()
    #print(mon.get_database('jianzhi'))
    #coll = mon.get_collection('test', 'test')
    #print(coll.find_one({'name': 'tim'}))