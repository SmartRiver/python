import pymongo
from pymongo import MongoClient
import sys
import jieba
import hashlib
import time



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

def fff(tt):
    tt[0] = 'b'
    

if __name__ == '__main__':
    
    aa = {'a', 'a', 'd', 'c'}

    bb = {'e', 'f'}

    cc = {
        'area':'jx',
        'id':2
    }

    dd = {
        'area':'jx',
        'id':3
    }


    bb.add(repr(cc))
    bb.add(repr(cc))
    bb.add(repr(dd))

    



    d = {'a':2, 'b':23, 'c':5, 'd':17, 'e':1}
    print(type(d))
    d2 = sorted(d.items(), key=lambda dddd:dddd[1], reverse=True)
    for each in d2:
        print(each[0])
    


