__author__ = '强胜'

import jieba
import re

if __name__ == '__main__':
    text = '如果放到post中将出错'
    jieba.add_word('post中')
    print(jieba.lcut(re.sub('[a-zA-z]+', ' ', text)) + re.findall('[a-zA-z]+', text))
