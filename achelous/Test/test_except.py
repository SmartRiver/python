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
	a=b=1
	yield a
	yield b
	while True:
		a, b = b, a+b
		yield b
		return 'xx'
if __name__ == '__main__':
	nums = [1,2,3,4,5,6]
	it = [i for i in nums]
	print(str(type(it)))

	for _ in range(10):
		print(_)
