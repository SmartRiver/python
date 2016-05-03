#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# date   : 2016/04/19

__author__ = 'johnson'
import urllib.request
import socket
from bs4 import BeautifulSoup
import time
import http.cookiejar
from urllib.parse import urlparse, urljoin
import re
import os
from urllib.parse import urlparse, urljoin

def test_socket(url):
    socket.setdefaulttimeout(20)
    #proxy_support = urllib.request.ProxyHandler({'http':'211.167.248.228:8080'})
    #cj = http.cookiejar.CookieJar()
    #opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    head = {
        'Connection': 'keep-alive',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Host': 'www.xicidaili.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    header = [] 
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    #opener.addheaders = header
    urllib.request.addheaders = header
    #urllib.request.install_opener(opener)
    response = urllib.request.urlopen(url)
    html = response.read()
    print(html)
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.title)
    print(time.time())
    time.sleep(10)
    print(int(time.time()))

def test():
    prefix = 'http://www.cornell.edu'
    

    #soup = BeautifulSoup(open('index.html', 'rb'), 'html.parser')
    soup = BeautifulSoup(open('index.html', 'rb'), 'html.parser')
    with open('index.html', 'rb') as f:
        fs = str(f.read())
    print(type(fs))
    fss = 'src="//media.univcomm.cornell.edu/photos/400x225/DD2A99F6-C94C-227D-B7A7217B732D61CF.jpg" jlsjdfljslj'
    

    reg = '[\\]["\']([https]{4,5}:)?/{1,2}[a-zA-Z0-9./\-?*&%#@]*[\\]?["\']'
    res = fs
    prefix = "http://www.cornell.edu"
    for each in re.finditer(reg, fs):
        href = each.group().strip('"')
        path = urljoin(prefix, href)
        path = urlparse(path)
        if path.hostname != None:
            if path.path.find('#') > 0 and path.path[0] == '#': # 忽略本网页链接
                continue
            path = os.getcwd()+'/cornell/'+ path.hostname + '/' + path.path
            path = path.replace('\\','/').replace('//', '/')
            if path.split('/')[-1].find('.') < 0:
                path += '/index.html'
            elif path.split('.')[-1].lower() in ['htm', 'dhtml', 'xhtml', 'shtm', 'shtml', 'asp', 'aspx', 'cfm', 'php', 'cgi', 'jsp', 'jspx']:
                path = path.replace('.'+path.split('.')[-1], '.html')
            path = path.replace('//','/')   
            
        res = res.replace(each.group(), '"'+path +'"').strip('b\'')
    
    res = res.replace(r'\r\n', '')
    xx = BeautifulSoup(res, 'html.parser')
    print(type(res))
    with open('result.html', 'w') as f:
        f.write(str(xx))

class Test:
    id = 2
    def __init__(self):
        self.id = 4
        self.name = 'first'
    def a(self):
        print(self.id)
    def set_name(self):

        self.name = 'hehe'

if __name__ == '__main__':
    #test_socket('http://www.xicidaili.com/')
    #test()
    # tt = '<tr valign="top" class="xx red"><td class="hot red">xx</td>ttt<td>yy</td></tr>'
    # soup = BeautifulSoup(tt, 'html.parser')
    # print(len(soup.find_all("tr", class_="xx")[0].contents))
    # if 'xx' in soup.find_all("tr", class_="xx")[0].contents:
    #     print(True)
    # for each in soup.find_all("tr", class_="xx"):
    #     print(type(each.contents[1]))
    test = Test()
    test.a()
    test.set_name()
    
    print(test.name)