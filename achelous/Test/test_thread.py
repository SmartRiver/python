#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xiaohe'

import threading
import time
mutex = threading.Lock()
counter = 0 
class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global counter
        time.sleep(1)
        if mutex.acquire():
            counter += 1
            print('%s\t%d' % (self.name, counter))
            mutex.release()



if __name__ == '__main__':
    for each in range(1,200):
        tt = MyThread()

        tt.start()