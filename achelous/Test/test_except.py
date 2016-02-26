__author__ = 'johnson'

def test_raise():
	
	try:
		
		print(1/0)
	except:
		raise NameError('hehe')

def aa():
	if 2 > 1:
		raise Exception('0 IS WRONG')
	else:
		return 2,3,4
def bb():
	if float('FDS'):
		raise Exception('can not ')
	

if __name__ == '__main__':
	try:
		a,b,c = aa()
		print('--%d--' % b)
	except Exception as e:
		
		print(str(type(e)))
		print('except:%s' % str(e))
	finally:
		print('returns')

	dicta = {'a': 1}
	dictb = {'b': 2}

	dicta.update(dictb)
	print(dicta)
	dictb['a'] = 3
	print(dicta)