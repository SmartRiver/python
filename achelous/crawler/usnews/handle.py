#!/usr/bin/python
#encoding:UTF-8
# date: 2015-04-29

__author__ = 'johnson'
__doc__ = '''this script is used to process result.json.'''

from pyexcel_xls import save_data
from collections import OrderedDict


if __name__ == '__main__':
    subject = set()
    xx = {}
    with open('result.json', 'r', encoding='UTF-8') as reader:
        for each in reader.readlines():
            record = eval(each.strip())
            subject.add(record['subject'])
            xx[record['subject']] = record['belong_to']
    tt = {}
    res = list()
    for each in subject:
        gg = []
        gg.append(each)
        gg.append(xx[each])
        res.append(gg)

    data = OrderedDict() # from collections import OrderedDict
    data.update({"Sheet 1": res})
    save_data("your_file.xls", data)