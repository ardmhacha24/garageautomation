import logging
from logging.handlers import RotatingFileHandler
import os
import errno
import sys

LOGFILE_FORMAT = '%(asctime)s [%(process)-5d:%(thread)#x] %(name)s %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
LOGFILE_MODE = 'a'
LOGFILE_MAXSIZE = 1 * 1024 * 1024
LOGFILE_BACKUP_COUNT = 10

# Set up logging
logger = logging.getLogger("garage_logs")
logger.setLevel(logging.DEBUG)
log_path = './garage_webserver.log'

file_handler = RotatingFileHandler(log_path,
                                   LOGFILE_MODE, \
                                   LOGFILE_MAXSIZE,
                                   LOGFILE_BACKUP_COUNT)
file_handler.setFormatter(logging.Formatter(LOGFILE_FORMAT))
logger.addHandler(file_handler)
#app.debug_log_format = '%(relativeCreated)-6d [%(process)-5d:%(thread)#x] %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
#app.logger.setLevel(logging.DEBUG)

if not os.path.exists(log_path):
    print("=======hkjjjkhkhkjhkh££%£$^^")
    #try:
    #   print ("=======hkjjjkhkhkjhkh££%£$^^")
    #   os.makedirs(os.path.dirname(log_path))
    #except OSError as exc:  # Guard against race condition
    #    if exc.errno != errno.EEXIST:
    #        raise

for _ in range(10):
    logger.info('---------- Starting up!')
    logger.info('__name__ is \'%s\'' % __name__)
    logger.debug('Loading default config file from \'%s\'' % log_path)
    logger.error('Looking for custom app config in \'%s\'' % log_path, 'app.cfg')

