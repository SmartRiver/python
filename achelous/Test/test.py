import pymongo
from pymongo import MongoClient
import sys
import jieba
import hashlib
import time
import urllib




def tt():
    ins_dict = {}
    for each in open('xxoo.txt', 'r', encoding='utf-8').readlines():
        each = each.strip('\r').strip('\n').split("|")[0]
        print(each)
        lis = jieba.lcut(each)
        str = ''
        for xx in lis:
            if xx not in ['学院', '学校', '高职', '大学', '分校', '分部', '校区']:
                str = str + '-'+xx
        ins_dict[each] = str.lstrip('-')


    writerr = open('gg.txt', 'w', encoding='utf-8')

    for each in ins_dict:
        writerr.write(ins_dict[each])
        writerr.write('\n')
    writerr = open('ggg.txt', 'w', encoding='utf-8')

    for each in ins_dict:
        writerr.write(each)
        writerr.write('\n')

def yxdaluan():
    ins_dict = {}
    for each in open('xxoo.txt', 'r', encoding='utf-8').readlines():
        each = each.strip('\r').strip('\n')
        header = each.split("|")[0]

def search(keyword, major=None, province=None):
    print('keyword: %s' % keyword)
    print('major: %s' % major)
    print('province: %s' % province)


def md5_check(token_key='dulishuo0306'):
    now = time.gmtime()
    key = 'dulishuo123'
    year = now.tm_year * 1
    month = now.tm_mon * 12
    day = now.tm_mday * 30
    hour = now.tm_hour * 60
    token_before = token_key+str(year+month+day+hour)
    m = hashlib.md5()
    m.update(token_before.encode('utf-8'))
    return m.hexdigest()[:16]

def fff():
    global aa
    aa = 6
    print(aa)
    print('-----')

def aaa():
    fff()
    print(aa)

def convert_to_str(input_origin):
    if isinstance(input_origin, bytes):
        return input_origin.decode('utf-8')
    elif isinstance(input_origin, str):
        input_origin = input_origin.replace(' ', '').replace('\'','').replace('"','')
        return input_origin
    elif isinstance(input_origin, (int, float)):
        return str(input_origin)
    elif input_origin == None:
        return input_origin
    else:
        try:
            return str(input_origin)
        except:
            return False

aa = None
if __name__ == '__main__':

    aa = ''.encode('utf-8')
    print(str(type(aa)))
    aa = convert_to_str(aa)
    print('-%s-' % aa)
