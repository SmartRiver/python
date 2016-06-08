import global_variable

from global_variable import INTERFACE_METHOD

def tt(each):
    print(each)

if __name__ == '__main__':
    for each in INTERFACE_METHOD:
        print(INTERFACE_METHOD[each])
        print(type(INTERFACE_METHOD[each]))
    xx = 'hello, word'
    yy = 'tt'
    if 2 > 1:
        exec(yy+'(xx)')
    
    str = '[(condition, 1, string),(major, 0, string),(area, 0, string),(country, 0, string)]'

       