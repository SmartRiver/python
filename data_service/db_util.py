# -*- coding: utf:-8 -*-

import pymongo
from pymongo import MongoClient
import logging
import logging.config

__author__ = 'xiaohe'
__doc__ = '''this py file is the collection of those operation functions or methods used in db'''


global db_logger # db logger

'''日志配置'''
def logging_conf():
    try:
        global db_logger
        logging.config.fileConfig('./conf/logging.conf')
        db_logger = logging.getLogger('general')
        db_logger.info('--------completing confuration--------')
    except Exception as e:
        print('--------logging configurating failed--------')

class MongoDB():
    def __init__(self, host, port, username=None, password=None, auth=False):
        #初始化类成员变量
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = auth
        #建立连接
        self._client_ = MongoClient(self.host, self.port)

        logging_conf()
        
    def get_database(self, db_name):
        self._db_name = self._client_[db_name]
        if self.auth:
            try:
                db_logger.info('mongodb authencating')
                if self._db_name.authenticate(self.username, self.password, mechanism='SCRAM-SHA-1'):
                    db_logger.info('authencation success.')
                    return self._db_name
                else:
                    db_logger.info('authencation failed.')
                    return False
            except:
                return False
        else:
            return self._db_name


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
        return self._collection_.insert_one(document).inserted_idc

    def close(self):
        self._client_.close()

def get_connection():
    client = MongoDB('123.57.250.189', 27017, username='dulishuo', password='Dulishuo123', auth=True)
    return client
