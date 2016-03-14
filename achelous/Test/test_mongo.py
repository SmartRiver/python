#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xiaohe'
import pymongo
from pymongo import MongoClient


if __name__ == '__main__':
    c = MongoClient('localhost', 27017)

    print('中国')

    test_collection = c['test']['test']

    test_collection.insert_one({'name': 'jim', 'id': 3})

    print(test_collection.find_one({'name': 'jim'}))

    test_collection.update_one({'name': 'jim'},{'$set':{'id':45}})

    print(test_collection.find_one({'name': 'jim'}))







    print('end . . . ')