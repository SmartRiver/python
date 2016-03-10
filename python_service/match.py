# -*- coding: utf-8 -*-
__author__ = 'Elliot'

import json
import math

OFFER_LIST = []
PROGRAM_REQUIREMENT = {}

def __init__():
    global OFFER_LIST
    global PROGRAM_REQUIREMENT
    # for line in open('resource/offer.json', 'rb'):
    #     print(line)
    #     print(json.loads(line))
    #     break
    OFFER_LIST = filter(
        lambda x: x['program_id'] != -1 and x['result'] ,
        map(
            lambda x: json.loads(x),
            open('resource/offer1.json', 'rb')
        )
    )
    for origin_program in map(
            lambda x: json.loads(x),
            open('resource/program_requirement.json', 'rb')
    ):
        PROGRAM_REQUIREMENT[origin_program['id']] = origin_program['exam_requirement']

def satisfy_requirement(exam_requirement, to_cmp):
    result = False

    for exam in ['toefl', 'ielts']:
        if exam_requirement[exam]['acceptable'] is not 1:
            continue
        temp_result = True
        for score_type in exam_requirement[exam]:
            if score_type == 'acceptable':
                continue
            if exam_requirement[exam][score_type] > to_cmp[exam][score_type]:
                temp_result = False
        if temp_result is True:
            result = True
            break

    return result

def fill_score(to_cmp):
    to_cmp['gre']['total'] = to_cmp['gre']['q'] + to_cmp['gre']['v']

    for exam in ['toefl', 'ielts']:
        total_score = to_cmp[exam]['total']
        if exam == 'ielts':
            total_score *= 4
        empty_count = 0
        for score_type in ['listening', 'reading', 'speaking', 'writing']:
            if score_type not in to_cmp[exam] or to_cmp[exam][score_type] is 0:
                to_cmp[exam][score_type] = 0
                empty_count += 1
            else:
                total_score -= to_cmp[exam][score_type]

        for score_type in ['listening', 'reading', 'speaking', 'writing']:
            if to_cmp[exam][score_type] is 0:
                to_cmp[exam][score_type] = total_score/empty_count

def offer_cmp(offer, to_cmp):
    dif = 0
    abs_dif = 0
    try:
        dif += (offer[u'gre'][u'total'] - to_cmp[u'gre'][u'total'])
        abs_dif += math.pow(offer[u'gre'][u'total'] - to_cmp[u'gre'][u'total'], 2)
        if offer[u'gpa'] is -1:
            dif = 10000
        dif += (offer[u'gpa'] - to_cmp[u'gpa']) * 5
        abs_dif += math.pow((offer[u'gpa'] - to_cmp[u'gpa']) * 5, 2)
    except KeyError:
        dif = 10000

    return {
        'dif': dif,
        'abs_dif': abs_dif,
    }

_IELTS_TOEFL = {
    4.0: 31,
    4.5: 34,
    5.0: 45,
    5.5: 59,
    6.0: 78,
    6.5: 93,
    7.0: 101,
    7.5: 109,
    8.0: 114,
    8.5: 117,
    9.0: 120,
}

_RANK_TYPE_BELONG = {
    1: 41,
    3: 38,
    2: 39,
    4: 37,
    5: 39,
    6: 41,
    7: 40,
    8: 41,
    9: 38,
    10: 39,
    11: 41,
    12: 40,
    14: 41,
    13: 41,
    15: 38,
    16: 38,
    17: 38,
    18: 38,
    20: 40,
    21: 40,
    22: 37,
    23: 41,
    24: 37,
    25: 40,
    26: 40,
    27: 39,
    28: 37,
    29: 39,
    30: 37,
    31: 40,
    32: 41,
    33: 39,
    34: 41,
    36: 39,
    35: 41,
    37: 42,
    38: 42,
    39: 42,
    40: 42,
    41: 42,
    19: 37,
}

def language_score(to_cmp):
    try:
        ielts_toefl = _IELTS_TOEFL[to_cmp[u'ielts'][u'total']]
    except KeyError:
        ielts_toefl = 0
    return max(ielts_toefl, to_cmp[u'toefl'][u'total'])

def offer_cmp_with_language(offer, to_cmp):
    dif = 0
    abs_dif = 0
    try:
        offer_language, to_cmp_language = language_score(offer), language_score(to_cmp)
        dif += offer_language - to_cmp_language
        abs_dif += math.pow(offer_language - to_cmp_language, 2)
    except KeyError:
        dif = 10000
    non_language = offer_cmp(offer, to_cmp)
    dif += non_language['dif']
    abs_dif += non_language['abs_dif']

    return {
        'dif': dif,
        'abs_dif': math.sqrt(abs_dif),
    }


def belong_category(child, parent):
    if parent is 42:
        return True
    return child is parent or child not in _RANK_TYPE_BELONG or _RANK_TYPE_BELONG[child] is parent


def find_nearest_offer(to_cmp, num=5, ocmp=offer_cmp_with_language):
    if 'rank_type_id' not in to_cmp:
        to_cmp['rank_type_id'] = 42
    offer_id_list = filter(
        lambda x: x[0]['dif'] < 5000 and belong_category(x[1]['rank_type_id'], to_cmp['rank_type_id']),
        map(
            lambda offer: (ocmp(offer, to_cmp), offer),
            OFFER_LIST
        )
    )
    # for offer in OFFER_LIST:
    #     dif = ocmp(offer, to_cmp)
    #     if dif['dif'] >= 10000:
    #         continue
    #     offer_id_list.append((dif, offer))
    offer_id_list.sort(
        cmp=lambda x, y: cmp(abs(x[0]['dif']), abs(y[0]['dif'])) if abs(x[0]['dif']) != abs(y[0]['dif']) else cmp(abs(x[0]['abs_dif']), y[0]['abs_dif'])
    )
    if num is -1 or len(offer_id_list) < num:
        return offer_id_list
    else:
        return offer_id_list[:num]


def find_program(to_cmp, num=5):
    useful_offer_list = filter(
        lambda x: satisfy_requirement(PROGRAM_REQUIREMENT[str(x[1]['program_id'])], to_cmp) is True and x[1]['result'] is not 3,
        find_nearest_offer(to_cmp, -1, offer_cmp)
    )
    program_id_list = []
    for offer_pair in useful_offer_list[:min(num*2, len(useful_offer_list))]:
        if offer_pair[1]['program_id'] not in program_id_list:
            program_id_list.append(offer_pair[1]['program_id'])
            if len(program_id_list) >= num:
                break
    return program_id_list

__init__()

