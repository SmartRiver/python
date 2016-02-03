# -*- coding: utf:-8 -*-
__author__ = 'xiaohe'
__doc__ = '''this py file is the collection of those functions or methods used in many other modules'''

def exit_error_func(error_param, error_code):
    error_dict = {
        1: '参数格式错误',
        2: '参数内容错误',
	    3: '程序内部错误'
    }
    return {
		'status': 'fail',
		'error': error_dict[error_code],
	    'msg': error_param,
    }