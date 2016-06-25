#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from global_variable import (GPA_SCHOOL_LEVEL, GPA_SCORE_LEVEL, SUBJECT_SCORE, IBT_LEVEL, GRE_LEVEL, GMAT_LEVEL, GMAT_TO_GRE, SCHOOL_LEVEL, MAJOR, SELECT_SCHOOL_TARGET_SCORE, SELECT_SCHOOL_OFFER_SCORE, INSTITUTE_ID_TO_NAME_EN, INSTITUTE_ID_TO_NAME_ZH, INSTITUTE_ID_TO_LOCATION, INSTITUTE_MAJOR_LEVEL, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER)
from common_func import (convert_var_type, convert_gre_to_gmat, convert_ielts_to_toefl, exit_error_func)
from db_util import MySqlDB
__author__  = 'johnson'
__doc__     = '''this script is used to match schools for student by assess the score of them'''

DATA_TEMPLATE = {   
    "major":8,
    "gpa":{"score":"3.5","school":"双非二本"},
    "gmat":{"total":"0","writing":"0"},
    "gre":{"total":"328","verbal":"160",
    "quantitative":"168","writing":"4"},
    "toefl":{"total":"106","speaking":"25"},
    "ielts":{"total":"0","speaking":"0"},
}

def evaluate_gpa(gpa_score, gpa_school=12):
    '''根据学校的本科学校档次不同，乘上一个系数'''
    gpa_school = convert_var_type(gpa_school, 'int')
    if gpa_school not in GPA_SCHOOL_LEVEL:
        raise KeyError('不包含该学校档次{}'.format(gpa_school))
    gpa_score = convert_var_type(gpa_score, 'float')
    return float('{:.2f}'.format(gpa_score*GPA_SCHOOL_LEVEL[gpa_school]))

def _student_data_check(student_data):
    '''检查用户数据是否完整、合法'''
    for first_key in DATA_TEMPLATE:
        if first_key not in student_data:
            raise KeyError('缺乏{0}数据，第一层键名为{0}'.format(first_key))
        if first_key == 'major':
            continue
        for second_key in DATA_TEMPLATE[first_key]:
            if second_key not in student_data[first_key]:
                raise KeyError('缺乏{0}的{1}数据，第二层键名为[{0}][{1}]'.format(first_key, second_key))

def _get_student_level(student_data, _temp_list, _major):
    '''根据学生三围成绩划分档次'''
    _temp_level = {
        'gpa'   : 5,
        'toefl_total' : 5,
        'ielts_total' : 5,
        'gre_total'   : 5,
        'gmat_total'  : 5,
    }
    for each in SELECT_SCHOOL_TARGET_SCORE[_major]:
        for score_key, score_value in _temp_list.items():
            if convert_var_type(score_value, 'float') > SELECT_SCHOOL_TARGET_SCORE[_major][each][score_key]:
                if _temp_level[score_key] > each:
                    _temp_level.update({score_key: each})
    _res_level = {
        'gpa' : _temp_level['gpa'],
        'it'  : min(_temp_level['toefl_total'], _temp_level['ielts_total']),
        'gg'  : min(_temp_level['gmat_total'], _temp_level['gre_total']),
    }
    return max(_res_level.values())

def _get_return_institute(_total_score, _major):
    '''按需求格式返回选校结果'''
    _suit_institute = {}
    for institute_key in SELECT_SCHOOL_OFFER_SCORE[_major]:
        if _total_score >= SELECT_SCHOOL_OFFER_SCORE[_major][institute_key]:
            _suit_institute.update({institute_key: SELECT_SCHOOL_OFFER_SCORE[_major][institute_key]})
    _sort_list = sorted(_suit_institute.items(), key=lambda x: x[1], reverse=True)
    
    _return_institute = []
    for item in _sort_list:
        _return_institute.append(item[0])
    return {
        'status': 'success',
        'result': _return_institute,
    }
    # _guarantee_institute    = []
    # _sprint_institute       = []
    # _suit_institute       = []
    # for each in qualified_institute:
    #     _temp_res = {
    #         'id': each,
    #         'name_en': INSTITUTE_ID_TO_NAME_EN[each],
    #         'name_zh': INSTITUTE_ID_TO_NAME_ZH[each],
    #         'location_type': INSTITUTE_ID_TO_LOCATION[each]
    #     }
    #     if _target_level == 1:
    #         if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
    #             _suit_institute.append(_temp_res)
    #         elif each in INSTITUTE_MAJOR_LEVEL[_major][_target_level+1]:
    #             _guarantee_institute.append(_temp_res)
    #     elif _target_level == 4:
    #         if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
    #             _suit_institute.append(_temp_res)
    #     else:
    #         if each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
    #             _suit_institute.append(_temp_res)
    #         elif each in INSTITUTE_MAJOR_LEVEL[_major][_target_level+1]:
    #             _guarantee_institute.append(_temp_res)
    
    # for each in INSTITUTE_MAJOR_LEVEL[_major][_target_level]:
    #     if each not in qualified_institute:
    #         _sprint_institute.append({
    #                 'id': each,
    #                 'name_en': INSTITUTE_ID_TO_NAME_EN[each],
    #                 'name_zh': INSTITUTE_ID_TO_NAME_ZH[each],
    #                 'location_type': INSTITUTE_ID_TO_LOCATION[each]
    #             })
    # return {
    #     'status':'success',
    #     'result':{
    #         'level': _target_level,
    #         'guarantee': _guarantee_institute,
    #         'sprint': _sprint_institute,
    #         'suit': _suit_institute
    #     }
    # }

def _get_gmat_gre(_temp_gre, _temp_gmat):
    '''将gmat转换为gre'''
    if _temp_gre < 260 and _temp_gmat >= 200:
        return GMAT_TO_GRE.get(_temp_gmat, GMAT_TO_GRE.get(_temp_gmat, VauleError('gmat分数不是有效的')))
    elif _temp_gmat >= 200 and _temp_gre > 260:
        if GMAT_TO_GRE.get(_temp_gmat, VauleError('gmat分数不是有效的')) > _temp_gre:
            return GMAT_TO_GRE.get(_temp_gmat, VauleError('gmat分数不是有效的'))
        else:
            return _temp_gre
    else:
        return _temp_gre

def _get_gre_gmat(_temp_gre, _temp_verbal, _temp_quantitative, _temp_gmat):
    '''将gre转换为gmat'''
    if _temp_gre >= 260:
        if _temp_verbal < 130 and _temp_quantitative >= 130:
            _temp_verbal = _temp_gre - _temp_quantitative
        if _temp_verbal >= 130 and _temp_quantitative < 130:
            _temp_quantitative = _temp_gre - _temp_verbal
    if _temp_verbal >= 130 and _temp_quantitative >= 130:
        _return = convert_gre_to_gmat(_temp_verbal, _temp_quantitative)
        if _return > _temp_gmat:
            return _return
        else:
            return _temp_gmat
    elif _temp_gmat > 200:
        return _temp_gmat
    else:
        return None

def _get_toefl_ielts(_toefl, _ielts):
    '''将ielts转化为toefl'''
    if _ielts > 0 and _toefl <= 0:
        return convert_ielts_to_toefl(_ielts)
    elif _ielts > 0 and _toefl > 0:
        if convert_ielts_to_toefl(_ielts) < _toefl:
            return _toefl
        else:
            return convert_ielts_to_toefl(_ielts)
    else:
        return _toefl

def get_offer_by_major(major_id):
    '''根据major_id获取所有offer案例'''
    my_sql = MySqlDB(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, 'hechuang')
    my_cursor = my_sql.get_cursor()
    sql_offer = 'select distinct(offer_id) from offer_result where major_id= %s'
    my_cursor.execute(sql_offer, ( major_id))
    result = my_cursor.fetchall()
    _return = []
    for each in result:
        _temp_offer_id = each['offer_id']
        _temp_sql = 'select max(gpa) from offer_edu_exp_major where edu_exp_id in (select id from offer_edu_exp where offer_id = %s)'
        my_cursor.execute(_temp_sql, _temp_offer_id)
        _gpa = my_cursor.fetchone()
        _gpa = _gpa['max(gpa)']
        if _gpa == None: # 过滤缺失gpa成绩的案例
            continue
        elif float(_gpa) <= 0.1:
            continue
        else:
            _gpa = float(_gpa)
        _temp_sql = 'select * from offer_hard_condition where offer_id = %s'
        my_cursor.execute(_temp_sql, (_temp_offer_id))
        _toefl_gre = my_cursor.fetchone()
        if _toefl_gre['toefl_total'] < 1 and _toefl_gre['ielts_total'] < 1: # 过滤同时缺失toefl和ielts成绩的案例
            continue
        elif _toefl_gre['gre_total'] < 260 and _toefl_gre['gmat_total'] < 200: # 过滤同时缺失gre和gmat成绩的案例
            continue
        
        _toefl_ielts = _get_toefl_ielts(_toefl_gre['toefl_total'], _toefl_gre['ielts_total'])
        if MAJOR[major_id]['belong_to'] == 4: # 商科的将gre转换为gmat成绩
            _gre_gmat = _get_gre_gmat(_toefl_gre['gre_total'], _toefl_gre['gre_verbal'], _toefl_gre['gre_quantitative'], _toefl_gre['gmat_total'])
            if _gre_gmat == None:
                continue
        else:
            _gre_gmat = _toefl_gre['gre_total']
            if _gre_gmat < 260:
                continue
        _temp_sql = 'select background_institute_level from offer_edu_exp where offer_id = %s'
        my_cursor.execute(_temp_sql, (_temp_offer_id))
        _institute_level = my_cursor.fetchone()['background_institute_level']
        if _institute_level not in SCHOOL_LEVEL:
            continue
        _return.append({
            'offer_id': _temp_offer_id,
            'institute_level': _institute_level,
            'gpa': _gpa,
            'gpa_absolute': float('{:.2f}'.format(_gpa * GPA_SCHOOL_LEVEL[SCHOOL_LEVEL[_institute_level]])),
            'gre_gmat': _gre_gmat,
            'toefl_ielts': _toefl_ielts
        })
    return _return
           
def _match(offer, _gpa, _toefl, _gre_gmat):
    '''将用户的三围成绩跟历史案例匹配'''
    if abs(offer['gpa_absolute'] - _gpa ) <= 0.1:
        if abs(offer['toefl_ielts'] - _toefl) <= 3:
            if abs(offer['gre_gmat'] - _gre_gmat) <= 5:
                return True
    return False           

def get_similar(**condition):
    '''寻找相似案例学生'''
    student_data = condition['condition']
    _student_data_check(student_data)
    _major = convert_var_type(student_data['major'], 'int')
    
    _gpa = evaluate_gpa(student_data['gpa']['score'], student_data['gpa']['school'])

    if convert_var_type(student_data['ielts']['total'], 'int') == 0 and convert_var_type(student_data['toefl']['total'], 'int') == 0:
        raise ValueError('雅思/托福 总分都没有')
    if convert_var_type(student_data['gre']['total'], 'int') < 260 and convert_var_type(student_data['gmat']['total'], 'int') < 200:
        raise ValueError('GRE/GMAT 总分都没有')
    
    _toefl = _get_toefl_ielts(int(student_data['toefl']['total']), float(student_data['ielts']['total']))
    if MAJOR[_major]['belong_to'] == 4: # 商科的将gre转换为gmat成绩
        _gre_gmat = _get_gre_gmat(int(student_data['gre']['total']), int(student_data['gre']['verbal']), int(student_data['gre']['quantitative']), int(student_data['gmat']['total']))
    else:
        _gre_gmat = _get_gmat_gre(int(student_data['gre']['total']), int(student_data['gmat']['total']))
    _offer = get_offer_by_major(_major)
    _return = []
    for each in _offer:
        if _match(each, _gpa, _toefl, _gre_gmat):
            _return.append(each)

    return {
        'status': 'success',
        'result': _return,
    }
    
def _get_toefl_ielts_score(_score, _full_score):
    for each in IBT_LEVEL:
        if int(each.split('-')[0]) <= _score <= int(each.split('-')[1]):
            return float('{:.2f}'.format(_full_score * IBT_LEVEL[each]))
    return None

def _get_gre_gmat_score(_score, _full_score, _major):
    _temp_rule = {}
    if MAJOR[_major]['belong_to'] == 4:
        _temp_rule = GMAT_LEVEL.copy()
    else:
        _temp_rule = GRE_LEVEL.copy()
    for each in _temp_rule:
        if int(each.split('-')[0]) <= _score <= int(each.split('-')[1]):
            return float('{:.2f}'.format(_full_score * _temp_rule[each]))
    return None

def _get_gpa_score(_score, _institute, _full_score):
    for each in GPA_SCORE_LEVEL:
        _temp_value = GPA_SCORE_LEVEL[each]
        if float(_temp_value.split('-')[0]) <= _score < float(_temp_value.split('-')[1]):
            _gpa_score = round(float(each) * _full_score * GPA_SCHOOL_LEVEL[_institute], 2)
    return _gpa_score

def assess_single(**condition):
    '''按照学生成绩匹配确切的院校'''
    student_data = condition['condition']
    _student_data_check(student_data)
    _major = convert_var_type(student_data['major'], 'int')
    if _major not in SELECT_SCHOOL_OFFER_SCORE:
        return exit_error_func(2, '数据库里没有与你匹配专业的案例')

    if convert_var_type(student_data['ielts']['total'], 'int') == 0 and convert_var_type(student_data['toefl']['total'], 'int') == 0:
        raise ValueError('雅思/托福 总分都没有')
    if convert_var_type(student_data['gre']['total'], 'int') < 260 and convert_var_type(student_data['gmat']['total'], 'int') < 200:
        raise ValueError('GRE/GMAT 总分都没有')
    
    _toefl = _get_toefl_ielts(int(student_data['toefl']['total']), float(student_data['ielts']['total']))
    if MAJOR[_major]['belong_to'] == 4: # 商科的将gre转换为gmat成绩
        _gre_gmat = _get_gre_gmat(int(student_data['gre']['total']), int(student_data['gre']['verbal']), int(student_data['gre']['quantitative']), int(student_data['gmat']['total']))
    else:
        _gre_gmat = _get_gmat_gre(int(student_data['gre']['total']), int(student_data['gmat']['total']))
    _full_score = SUBJECT_SCORE.get(MAJOR[_major]['name_en'], '35-30-25')
    _gpa_score = _get_gpa_score(float(student_data['gpa']['score']), convert_var_type(student_data['gpa']['school'], 'int'), int(_full_score.split('-')[0]))
    _toefl_ielts_score = _get_toefl_ielts_score(_toefl, int(_full_score.split('-')[1]))
    _gre_gmat_score = _get_gre_gmat_score(_gre_gmat, int(_full_score.split('-')[2]), _major)

    _total_student_score = sum([_gpa_score, _toefl_ielts_score, _gre_gmat_score])

    # _temp_list = {
    #     'gpa'           : gpa, 
    #     'ielts_total'   : student_data['ielts']['total'],
    #     'toefl_total'   : student_data['toefl']['total'], 
    #     'gre_total'     : student_data['gre']['total'],
    #     'gmat_total'    : student_data['gmat']['total'],
    # }

    # if _major not in SELECT_SCHOOL_TARGET_SCORE:
    #     _major = -1
    # _target_level = _get_student_level(student_data, _temp_list, _major)

    # qualified_institute = []
    # for each_institute in SELECT_SCHOOL_OFFER_SCORE[_major]:
    #     _temp_level = {
    #     'gpa'   : 0,
    #     'toefl_total' : 0,
    #     'ielts_total' : 0,
    #     'gre_total'   : 0,
    #     'gmat_total'  : 0,
    #     }
    #     for each_element in _temp_level:
    #         _temp = SELECT_SCHOOL_OFFER_SCORE[_major][each_institute][each_element]
    #         if _temp < 0.1:
    #             continue
    #         if float(_temp_list[each_element]) > _temp:
    #             _temp_level[each_element] = 1
    #     # 判断是否达到该院校分数要求
    #     if _temp_level['gpa'] == 1:
    #         if (_temp_level['toefl_total'] + _temp_level['ielts_total']) >= 1:
    #             if (_temp_level['gre_total'] + _temp_level['gmat_total']) >= 1:
    #                 qualified_institute.append(each_institute)
    try:
        return _get_return_institute(_total_student_score, _major)
    except Exception as e:
        return exit_error_func(3, str(e))
    
    








