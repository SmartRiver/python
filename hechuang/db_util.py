# -*- coding: utf:-8 -*-

import pymongo
from pymongo import MongoClient
import logging
import logging.config
import pymysql


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

    def __del__(self):
        self._client_.close()


class MySqlDB(object):
    def __init__(self, host, port, user, password, db):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__db   = db

    def get_connection(self):
        '''creating a connection to the database. '''
        self.__connection = pymysql.connect(  host=self.__host,
                                            port=self.__port,
                                            user=self.__user,
                                            password=self.__password,
                                            db=self.__db,
                                            charset='utf8',
                                            cursorclass=pymysql.cursors.DictCursor)
        return self.__connection

    def get_cursor(self):
        '''Return a new Cursor Object using the connection. '''
        if not hasattr(self, '__connection'):
            return self.get_connection().cursor()
        return self.__connection.cursor()

    def __del__(self):
        self.__connection.close()
        print('mysql connection close.')

def get_offercase_by_institute_and_major(institute_id, major_id):
    offercase = []
    my_db = MySqlDB()


