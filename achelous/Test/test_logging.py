__author__ = 'johnson'

import logging
import logging.config
import time

logging.config.fileConfig('logging.conf')

# create logger
loggerc = logging.getLogger('root.a')
loggera = logging.getLogger('root')
loggerb = logging.getLogger('root')
loggerd = logging.getLogger('root.simple')
loggere = logging.getLogger('simple')

f = logging.Filter('root')
loggerc.addFilter(f)

#print(loggerc.__dict__)
#print(loggerc.filters)

loggera.debug('root debug message')
loggera.info('rpoot info message')

print(id(loggera))
print(id(loggerb))
print(id(loggerc))
print(id(loggera.getChild('a')))
print(id(loggerd))
print(id(loggere))


start_time = time.time()
# 'application' code

loggerc.debug('debug me反反我是你加他复复sage'.decode('utf-8'))
loggerc.info('info message')

end_time = time.time()
print('use time: %d s.' % (end_time-start_time))