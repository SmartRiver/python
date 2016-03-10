# -*- coding: utf-8 -*-
__author__ = 'Elliot'

import jieba
import re
import csv
import logging
from django.utils.encoding import smart_str, smart_unicode

FULL_DICT = {}
STOP_WORDS = set()

# FULL_DICT = {
#     'school': [
#         {
#             'value': 239,
#             'keyword': {u'普林斯顿大学'},
#             'regex': [],
#             'entity': set(),
#         },
#         {
#             'value': 303,
#             'keyword': set(),
#             'regex': [u'Washington University in St. Louis'],
#             'entity': set(),
#         },
#     ]
# }


def __init__():
    global FULL_DICT
    temp_full_dict = {
        # u'test': [],
        u'question': [],
        u'assessment-factor': [],
        # u'application': [],
        u'school': [],
        u'faculty': [],
        u'program': [],
        u'country': [],
        u'location': [],
        u'rank-source': [],
        u'keyword': [],
        u'faculty-type': [],
        u'location-field': [],
        u'school-field': [],
        u'faculty-field': [],
        u'program-field': [],
    }
    global STOP_WORDS
    # dict init
    for theme in temp_full_dict:
        print(theme)
        dict_reader = csv.reader(open('resource/sym_dict/' + theme + '.csv', 'rb'))
        rule_list = []
        for origin_rule in dict_reader:
            if len(origin_rule) < 2:
                continue
            rule_dict = {}
            try:
                rule_dict['value'] = int(origin_rule[0])
            except ValueError:
                rule_dict['value'] = smart_unicode(origin_rule[0])

            for rule_type in ['keyword', 'regex', 'entity']:
                rule_dict[rule_type] = list(map(
                    lambda x: smart_unicode(x)[len(rule_type) + 1:],
                    filter(
                        lambda x: x.find(rule_type) is 0,
                        origin_rule[1:]
                    )
                ))

            for rule_type in ['keyword']:
                rule_dict[rule_type] = list(map(
                    lambda x: x.lower(),
                    rule_dict[rule_type]
                ))

            for rule_type in ['keyword', 'entity']:
                rule_dict[rule_type] = set(rule_dict[rule_type])

            rule_list.append(rule_dict)
        temp_full_dict[theme] = rule_list

    # cut dict
    for theme in FULL_DICT:
        for rule_dict in FULL_DICT[theme]:
            for keyword in rule_dict['keyword']:
                jieba.add_word(keyword)
    jieba.load_userdict('resource/jieba_dict/other_dict.txt')

    temp_stop_words = set(
        map(
            lambda x: x.strip().decode('utf-8'),
            open('resource/jieba_dict/stop_word_dict.txt').readlines()
        ) +
        [u' ']
    )
    print('Dicts are successfully loaded!')
    FULL_DICT = temp_full_dict
    STOP_WORDS = temp_stop_words


def add_property(text_dict, theme, is_force=False):
    if theme not in FULL_DICT or not isinstance(text_dict, dict) or 'text' not in text_dict:
        return False
    if 'property-dict' not in text_dict:
        text_dict['property-dict'] = {}
    if theme not in text_dict['property-dict']:
        text_dict['property-dict'][theme] = []
    elif is_force is False:
        return False
    if 'word-set' not in text_dict:
        text_dict['word-set'] = text2word_set(text_dict['text'])
    if 'entity-set' not in text_dict:
        text_dict['entity-set'] = set()

    rule_list = FULL_DICT[theme]

    for rule_dict in rule_list:
        if rule_dict['entity'].issubset(text_dict['entity-set']) is False:
            continue
        if rule_dict['keyword'].issubset(text_dict['word-set']) is False:
            continue
        temp_flag = True
        for regex in rule_dict['regex']:
            try:
                if not re.search(regex, text_dict['text']):
                    temp_flag = False
                    break
            except re.error:
                logging.warning("invalid regex: " + regex)
                temp_flag = False
                break
        if temp_flag is True:
            text_dict['property-dict'][theme].append(rule_dict['value'])
            text_dict['entity-set'].add(theme)
            text_dict['entity-set'].add(theme + u':' + smart_unicode(rule_dict['value']))


def text2word_set(text):
    return set(map(
        lambda x: x.lower(),
        jieba.lcut(re.sub('[a-zA-z]+', ' ', text)) + re.findall('[a-zA-z]+', text)
    )) - STOP_WORDS


def quest2quest_dict(quest):
    # process assessment
    assessment_property_dict = {}
    if quest.split(' ')[0] == u'选校':
        factor_list = quest.split(' ')[1:]
        for factor in factor_list:
            try:
                factor_name, factor_value = factor.split(':')
                factor_dict = {
                    'text': factor_name,
                    'word-set': set()
                }
                add_property(factor_dict, 'assessment-factor')
                if factor_dict['property-dict']['assessment-factor']:
                    factor_name = factor_dict['property-dict']['assessment-factor'][0]
                assessment_property_dict[factor_name] = float(factor_value)
            except:
                'Nothing'
        return {
            'property-dict': assessment_property_dict,
            'type': 'assessment',
        }

    quest_dict = {
        'text': quest,
        'word-set': text2word_set(quest)
    }
    # process special question
    add_property(quest_dict, 'question')
    if quest_dict['property-dict']['question']:
        return {
            'property-dict': quest_dict['property-dict'],
            'type': 'question',
        }

    for basic_theme in ['school', 'country', 'faculty',
                        'program', 'location', 'rank-source', 'faculty-type', 'assessment-factor']:
        add_property(quest_dict, basic_theme)

    if quest_dict['property-dict']['rank-source']:
        if quest_dict['property-dict']['faculty-type']:
            quest_dict['property-dict']['rank-source'] = ['qs']
        elif 'us-news' in quest_dict['property-dict']['rank-source']:
            quest_dict['property-dict']['rank-source'] = ['us-news']
        else:
            quest_dict['property-dict']['rank-source'] = ['qs']

    for keyword_theme in ['school-field', 'program-field', 'faculty-field', 'location-field', 'keyword']:
        add_property(quest_dict, keyword_theme)

    quest_type = 'other'
    # Entity
    if quest_dict['property-dict']['school']:
        if quest_dict['property-dict']['program']:
            quest_type = 'program'
        elif quest_dict['property-dict']['faculty']:
            quest_type = 'faculty'
        else:
            quest_type = 'school'
    elif quest_dict['property-dict']['location']:
        quest_type = 'location'
    elif quest_dict['property-dict']['rank-source']:
        quest_type = 'ranking'

    # Entity Field
    if quest_type != 'other':
        if quest_type + '-field' in quest_dict['property-dict'] \
                and quest_dict['property-dict'][quest_type + '-field']:
            quest_type += '-field'
        if quest_dict['property-dict']['keyword']:
            quest_type += '-keyword'
    elif quest_type != 'ranking':
        if quest_dict['property-dict']['keyword']:
            # Keyword
            quest_type = 'keyword'
        for theme in ['school', 'faculty', 'program', 'location']:
            if quest_dict['property-dict'][theme + '-field']:
                quest_type = 'keyword:' + theme
                break

    remove_list = []
    for theme in quest_dict['property-dict']:
        if not quest_dict['property-dict'][theme]:
            remove_list.append(theme)
    for theme in remove_list:
        del quest_dict['property-dict'][theme]
    return {
        'type': quest_type,
        'property-dict': quest_dict['property-dict'],
    }

__init__()


