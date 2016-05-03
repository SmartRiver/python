#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xiaohe'

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import json


@gen.coroutine
def post(self):
    resp = yield GetUser()
    self.write(resp)

@gen.coroutine
def GetUser():
    client = AsyncHTTPClient()
    resp = yield client.fetch("https://api.github.com/users")
    if resp.code == 200:
        resp = escape.json_decode(resp.body)
    else:
        resp = {"message": "fetch client error"}
        logger.error("client fetch error %d, %s" % (resp.code, resp.message))
    raise gen.Return(resp)

def xx():
    for each in range(3):

        print('before:'+str(each))
        yield 1+2
        print('after:'+str(each))
if __name__ == '__main__':
    urll = 'https://github.com/tornadoweb/tornado/blob/master/tornado/httpclient.py'
    tt = xx()
    print(type(tt))
    for each in range(3):
        print('-------------')
        tt.next()