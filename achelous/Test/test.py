import pymongo
from pymongo import MongoClient
import sys
import jieba
import hashlib
import time
import urllib
import hash



def _timestamp_check(timestamp_client):
    now_time = int(time.time())
    if -300 < now_time-timestamp_client < 300:
        return True
    else:
        return False

def pre_token_check(client_token):
    if not isinstance(client_token, str):
        raise Exception('参数应为字符串格式')
    if len(client_token) < 26:
        raise Exception('参数字符位数不小于26位')

def md5_token(client_token):
    key_a = 1237 # 质数因子
    key = '100117108105115104117111' # key = ''.join(str(ord(x)) for x in 'dulishuo') 额外的关键字

    try:
        pre_token_check(client_token)
        msg_client = client_token[:16]
        timestamp_client = client_token[16:26]

        timestamp_client = int(timestamp_client)
        if not _timestamp_check(timestamp_client):
            return False
        # 取年月日小时
        client_time = time.gmtime(timestamp_client)
        year = client_time.tm_year
        month = client_time.tm_mon
        day = client_time.tm_mday
        hour = client_time.tm_hour

        token_str = ''.join(str(int(x) * key_a) for x in [year, month, day, hour])
        token_str = token_str+key
        #md5加密
        m = hashlib.md5()
        m.update(token_str.encode('utf-8'))
        token_m = m.hexdigest()[:16]
        print(('token_m:'+token_m))

        if msg_client == token_m:
            return True
        else:
            return False
    except Exception as e:
        #raise Exception(exit_error_func(6, str(e)))
        return False




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
def test_token():
        client_time = time.gmtime(time.time())
        print(client_time)
        key_a = 1237 # 质数因子
        key = '100117108105115104117111' # key = ''.join(str(ord(x)) for x in 'dulishuo') 额外的关键字
        year = client_time.tm_year
        month = client_time.tm_mon
        day = client_time.tm_mday
        hour = client_time.tm_hour

        token_str = ''.join(str(int(x) * key_a) for x in [year, month, day, hour])
        token_str = token_str+key

        #md5加密
        m = hashlib.md5()
        m.update(token_str.encode('utf-8'))
        token_m = m.hexdigest()[:16]


        token_server = ''.join(token_m)
        token_server = token_server + str(int(time.time()))
        print(str(int(time.time())))
        print('token_server:'+token_server)
        #time.sleep(32)
        print('sleep end')
        print(md5_token('f6e5ec9928c65d2c1456715513'))

if __name__ == '__main__':
<<<<<<< Updated upstream
    if 3 >= 3:
        print(True)
=======
    a = 'dfdsafdf<br>活动经历<br>'
    print(a.replace('<br>活动经历<br>', ''))
>>>>>>> Stashed changes
