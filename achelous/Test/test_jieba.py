__author__ = '强胜'

import jieba

for each in open('university_dict.txt', 'r', encoding='utf-8').readlines():
    each = each.strip('\r').strip('\n')
    print(jieba.lcut(each))
