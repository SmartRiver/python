# -*- coding: utf:-8 -*-
import json
import codecs
import sys
 
reload(sys)   
sys.setdefaultencoding('utf8')

def translateFromFrontToBack(translateDict):
    file = codecs.open('translator.txt', 'r', 'utf-8')
    originDict = {}
    title = ""
    subTitle = ""
    content = {}
    tempDict = {}
    type = 0
    mismatch_list = []
    while 1:
        line = file.readline().strip().strip('\n').strip('\t')
        if not line:
            break
        if len(line.strip()) == 0:
            continue
        if line.count(":") == 1 and line.count("|") == 0:
            if not len(title) == 0:
                originDict[title] = content;
            if not title == line.split("|")[0]:
                content = {}
            title = line.split(":")[0]
            tempDict = {}
            type = 0
        elif line.count(":") == 1 and line.count("|") == 1:
            if not len(title) == 0:
                originDict[title] = content;
            if not title == line.split("|")[0]:
                content = {}
            title = line.split("|")[0]
            subTitle = line.split("|")[1].split(":")[0]
            tempDict = {}
            type = 1
        else:
            if type == 0:
                content[line.split(',')[0]] = line.split(',')[1]
            else:
                tempDict[line.split(',')[0]] = line.split(',')[1]
                content[subTitle] = tempDict;
    replace(originDict, translateDict, mismatch_list)
    return {
        'result': translateDict,
        'mismatch': mismatch_list,
    }

def replace(originDict, translateDict, mismatch_list):
    exception = ""
    key = ""
    sub_key = ""

    if 'major' in translateDict:
        if translateDict['major'] == "法学" or translateDict['major'] == 'law':
            if 'current-school' in translateDict:
                originDict['current-school'] = {
                    '清华北大':'0',
                    '985院校':'1',
                    '211院校':'3',
                    '专业优势学校':'2',
                    '海外本科': '1',
                    '非211非985':'5'
                }
    #遍历带翻译的字典，获取键
    for translateDictKey in translateDict:
        #根据键判断该键所映射值是否为字典
        if isinstance(translateDict[translateDictKey], dict):
            #如果该键对应的值是字典，则将键记录下来
            key = translateDictKey#key 如 major
            #然后继续找到该子字典的键
            for translateDictSubKey in translateDict[key]:
                #在translateDict中，字典的深度为2，所以到此为止即可
                sub_key = translateDictSubKey#sub_key 如 total
                #开始检查参考字典是否具有相应结构
                #第一层
                if key in originDict:
                    #第二层
                    #首先检查是否为字典
                    if isinstance(originDict[key], dict):
                        #然后检查是否有相应的键
                        if sub_key in originDict[key]:
                            #如果有键，则去参考字典第三层寻找有没有对应该键值的键
                            if translateDict[key][sub_key] in originDict[key][sub_key]:
                               #如果有，则将待翻译的值翻译成参考字典中相应的值
                                value = originDict[key][sub_key][translateDict[key][sub_key]]
                               #如果值可以转化为浮点数,则转化为浮点数
                                if value.replace(".","").isdigit() and value.count(".") == 1:
                                    value = float(value)
                                elif value.isdigit():
                                    value = int(value)
                                else:
                                    pass
                                translateDict[key][sub_key] = value
                            else:
                                if len(translateDict[key][sub_key].strip()) != 0:
                                    mismatch_list.append(key+':'+sub_key)

        else:
            #第一次遍历时该键所对应的就是基础值
            #根据该键去对照参考字典
            #首先判断参考字典是否有该键
            if translateDictKey in originDict:
                #如果有键，则去参考字典寻找有没有对应该键值的键
                #值由字典组成
                if translateDict[translateDictKey] in originDict[translateDictKey]:
                    #如果有，则将待翻译的值翻译成参考字典中相应的值
                    value = originDict[translateDictKey][translateDict[translateDictKey]]
                    #如果值可以转化为浮点数,则转化为浮点数
                    if value.replace(".","").isdigit() and value.count(".") == 1:
                        value = float(value)
                    elif value.isdigit():
                        value = int(value)
                    else:
                        pass
                    translateDict[translateDictKey] = value
                else:
                    if len(translateDict[translateDictKey].strip()) != 0:
                        mismatch_list.append(translateDictKey)
