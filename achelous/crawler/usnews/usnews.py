#!/usr/bin/python
#encoding:UTF-8
# date: 2015-04-29

__author__ = 'johnson'
__doc__ = '''this script is used to fetch all subject ranking infomation from US-NEWS.'''
            
import urllib.request
import http.cookiejar
from urllib.parse import quote
import urllib.response
from bs4 import BeautifulSoup
import json
import time
import os
import sys
import logging
import logging.config
from pyexcel_xls import get_data

class Crawler:
    def __init__(self):
        self.__login()

    # head: dict of header
    def __makeMyOpener(self):
        head = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        cj = http.cookiejar.CookieJar()
        self.__opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        self.__opener.addheaders = header

    def __login(self):
        '''login usnews.com'''
        self.__makeMyOpener()
        login_url = 'https://secure.usnews.com/member/login'
        username = 'andrew.liang@dulishuo.com'
        password = 'Lcy19930524!'
        postDict = {
            'username': username,
            'password': password,
            'referer': '',
        }
        postData = urllib.parse.urlencode(postDict).encode()
        op = self.__opener.open(login_url, postData)
        if op.getcode() == 200:
            logging.info('login success !')
        else:
            logging.info('login fail !')
            logging.error('exit script !')
            exit(-1)

    def __fetch(self, url, count=1):
        '''get the content of url'''
        uop = self.__opener.open(url, timeout = 1000)
        data = uop.read().decode('UTF-8')
        if uop.getcode() == 200:
            logging.info('fetch %s success !' % url)
        else:
            logging.info('fetch %s fail !' % url)
            logging.info('retry fetch %d times . . .' % count)
            count += 1
            if count > 10:
                logging.error('exit script !')
                exit(-1)
            return self.__fetch(url, count+1)
        return data

    def __get_total_pages(self, pager_link):
        '''get the total pages'''
        res = 1
        for each in pager_link:
            try:
                if str(each.string).isdigit():
                    page = int(each.string)
                    if page > res:
                        res = page
            except Exception as e:
                logging.error('get the total pages wrong !')
                logging.error(e)
        return res
    def __parse_detail(self, data, subject):
        soup = BeautifulSoup(data, 'html.parser', from_encoding='utf-8')
        global SUBJECT
        with open('result.json', 'a', encoding='utf-8') as fw:
            for each in soup.find_all("tr", attrs={"valign": "top"}):
                try:
                    rank_tag = each.find_all("td")[1].select("span")[0].contents
                    if len(rank_tag) > 1:
                        rank = str(rank_tag[1]).strip()
                    else:
                        rank = str(rank_tag[0]).strip()
                    name = str(each.find_all("td")[2].find_all("a")[0].string).strip()
                    rank_info = {}
                    rank_info['subject'] = subject
                    if subject in SUBJECT:
                        rank_info['belong_to'] = SUBJECT[subject]
                    else:
                        rank_info['belong_to'] = ''
                    rank_info['value'] = rank
                    rank_info['name'] = name
                    fw.write(str(rank_info)+'\n')
                except Exception as e:
                    logging.error(str(e))
                    logging.error('wrong line : %d \n exit script !' % str(each))
                    exit(-1)
                

    def parse(self, url, subject):
        '''parse the content, and get the list of rank info.'''
        data = self.__fetch(url)
        soup = BeautifulSoup(data, 'html.parser', from_encoding='utf-8')      
        pages = self.__get_total_pages(soup.select('.pager_link'))
        logging.info('total pages : %d' % pages)
        self.__parse_detail(data, subject)
        for each in range(2, pages+1):
            self.__parse_detail(self.__fetch(url+'/page+'+str(each)), subject去22    )

    def parse_batch(self, url_batch):
        '''batch process url request'''
        for each in url_batch:
            self.parse(url_batch[each], each)
            time.sleep(1) # sleep 1s between each process task

def read_urls():
    '''get the urls of all subjects from conf file url.txt'''
    url = {}
    global SUBJECT
    try:
        data = get_data('url.xlsx', streaming=True)
    except Exception as e:
        logging.error(str(e))
        logging.error('file read failed !')
        exit(-1)
    for each in data:
        url[each[0].strip()] = each[2].strip()
        SUBJECT[each[0].strip()] = each[1].strip()
    return url

SUBJECT = {} # 专业的对应从属关系字典

def _logging_conf():
    logging.basicConfig(level=logging.INFO,  
        format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='> ',
        filename='logging.log',
        filemode='w')

if __name__ == '__main__':
    _logging_conf()
    
    url = read_urls()
    crawler = Crawler()
    crawler.parse_batch(url)

    logging.info('end . . . ')

