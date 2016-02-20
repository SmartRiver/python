import pymongo
from pymongo import MongoClient
import sys
import jieba


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

if __name__ == '__main__':
    search('jjhh', 'cs', 'jiangxi')
    search(province='jianxi', keyword='jjhh')