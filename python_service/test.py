# -*- coding: utf-8 -*-
__author__ = 'Elliot'

from quest_process import quest2quest_dict
from quest_process import add_property
from django.utils.encoding import smart_str, smart_unicode
import csv


def _print_quest_dict(quest_dict):
    print(quest_dict['property-dict'])
    print(quest_dict['type'])


def test_for_q2qd():
    for origin_dict in csv.DictReader(open('resource/labeled_question.csv', 'rb')):
        quest_dict = quest2quest_dict(smart_unicode(origin_dict['question']))
        print(smart_unicode(origin_dict['question']))
        print(quest_dict['type'] == origin_dict['type'])
        _print_quest_dict(quest_dict)
        raw_input()


def test_for_classify():
    labeled_question_list = map(
        lambda x: (quest2quest_dict(smart_unicode(x['question']))['word-set'], x['type']),
        csv.DictReader(open('resource/labeled_question.csv', 'rb'))
    )

    for labeled_question in labeled_question_list:
        print(labeled_question)
        raw_input()


def test_for_add_property():
    quest_dict = {
        'text': u'qs试一发'
    }
    add_property(quest_dict, 'test')
    print()

test_for_q2qd()
