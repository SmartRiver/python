# -*- coding: utf:-8 -*-

__author__ = 'xiaohe'
__doc__ = '''this py file is the collection of those functions or methods used in many other modules'''

def exit_error_func(error_code, error_param=''):
    error_dict = {
		1: '参数格式错误',
	    2: '参数内容错误',
	    3: '程序内部错误',
    }
    return {
	    'status': 'fail',
	    'error': error_dict[error_code],
	    'msg': error_param,
	}
def convert_to_str(input_str):
    if str(type(input_str)).find('bytes') > 0:
        return input_str.decode('utf-8')
    else:
        return input_str
def token_check(token_string):
	pass