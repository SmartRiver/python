#!/usr/bin/python
# -*- coding: utf-8 -*-
#date   : 2016/01/22
__author__ = 'xiaohe'
__doc__ = ''' this Script file is used to crawler data from http://zzys.agri.gov.cn/'''

from selenium import webdriver
import time
import json

#页面抓取和提取信息函数
#def crawler(url):


if __name__ == "__main__":
    start = time.time()
    print('start . . . ')

    province_dict = {
    	u'北京':11,
		u'新疆':65,
		u'重庆':49,
		u'广东':44,
		u'浙江':33,
		u'天津':12,
		u'广西':45,
		u'内蒙古':15,
		u'宁夏':64,
		u'江西':36,
		u'贵州':52,
		u'安徽':34,
		u'陕西':61,
		u'辽宁':21,
		u'山西':14,
		u'青海':63,
		u'四川':51,
		u'江苏':32,
		u'河北':13,
		u'西藏':54,
		u'福建':35,
		u'吉林':22,
		u'云南':53,
		u'上海':31,
		u'湖北':42,
		u'海南':46,
		u'全国':0,
		u'甘肃':62,
		u'湖南':43,
		u'山东':37,
		u'河南':41,
		u'黑龙江':23,
    }

    fruit_dict = {
    	u'水果':11,
		u'香蕉':15,
		u'柿子':23,
		u'荔枝':17,
		u'苹果':12,
		u'桃':19,
		u'菠萝':16,
		u'葡萄':21,
		u'梨':13,
		u'龙眼':18,
		u'红枣':22,
		u'猕猴桃':20,
		u'柑橘类':14,
    }

    vegetable_dict = {
    	u'蔬菜':1,
		u'白菜':2,
		u'大白菜':3,
		u'普通白菜':4,
		u'甘蓝':5,
		u'花椰菜':6,
		u'芹菜':7,
		u'菠菜':8,
		u'莴苣':9,
		u'蕹菜':10,
		u'苋菜':11,
		u'芥菜':12,
		u'萝卜':13,
		u'胡萝卜':14,
		u'马铃薯':15,
		u'姜':16,
		u'芋':17,
		u'大蒜':18,
		u'大葱':19,
		u'洋葱':20,
		u'韭菜':21,
		u'藠头':22,
		u'蕃茄':23,
		u'茄子':24,
		u'辣椒':25,
		u'甜椒':26,
		u'菜豆':27,
		u'豇豆':28,
		u'黄瓜':29,
		u'冬瓜':30,
		u'南瓜':31,
		u'丝瓜':32,
		u'苦瓜':33,
		u'莲藕':34,
		u'茭白':35,
		u'金针菜':36,
		u'芦笋':37,
		u'竹笋':38,
		u'草莓':39,
		u'其他':40,
    }

    for each in vegetable_dict:
    	print('vegetable.put("'+each+'",'+str(vegetable_dict[each])+');')

    #vegetable_writer.flush()
    #vegetable_writer.close()

    # fruit_writer = open('fruit.txt','w')
    # vegetable_writer = open('vegetable.txt','w')
    # for year in range(1949,2015):
    # 	for ttype in range(1,3):
    # 		for province_key in province_dict:
    # 			for fruit_key in fruit_dict:
    # 				url = 'http://zzys.agri.gov.cn/shuiguo_cx_result.aspx?year='+year+'&prov='+province_dict[province_key]+'%20%20%20&item='+fruit_dict[fruit_key]+'&type='+ttype+'&radio=1&order1=year_code&order2=prov_code&order3=item_code';
    # 				result['year'] = year
    # 				result['province_id'] = province_dict[province_key]
    # 				result['province'] = province_key
    # 				result['fruit_id'] = fruit_dict[fruit_key]
    # 				result['fruit'] = fruit_key
    # 				result['amount'] = crawler(url)
    # 				fruit_writer.write(str(result))