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
		a = 1/0
	except Exception as e:
		try:
			print("----")
		except:
			print('----end----')
		