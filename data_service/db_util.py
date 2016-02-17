# -*- coding: utf:-8 -*-

__author__ = 'xiaohe'
__doc__ = '''this py file is the collection of those operation functions or methods used in db'''

class MongoDB():
    _client_ = ''
    _database_ = ''
    _collection_ = ''
    
    host = ''
    port = ''
    database = ''
    username = ''
    password = ''
    collection = ''
    
    def __init__(self, host, port, database, collection, username=None, password=None):
        #初始化类成员变量
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.collection = collection
        
        #建立连接
        self._client_ = MongoClient(self.host, self.port)
        self._database_ = self.client[self.database]
        if self._database_.authenticate(username, password, mechanism='MONGODB-CR'):
            self._collection_ = self._database_[self.collection]
            print(self._collection_)
        else:
            print('用户名/密码/验证方式错误')
    
    def findOne(self):
        return self._collection_.find_one()
        
    def insertOne(self, document):
        return self._collection_.insert_one(document).inserted_id