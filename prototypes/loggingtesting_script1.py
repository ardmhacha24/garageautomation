import logging
import os
import errno
import sys

LOGFILE_FORMAT = '%(asctime)s [%(process)-5d:%(thread)#x] %(name)s %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
LOGFILE_MODE = 'a'
LOGFILE_MAXSIZE = 1 * 1024 * 1024
LOGFILE_BACKUP_COUNT = 10

# Set up logging
logger = logging.getLogger("garage_logs")
log_path = './testing/garage_webserver.log'

# app.logger_name = "WEBSRVR"
file_handler = RotatingFileHandler(log_path,
                                   LOGFILE_MODE, \
                                   LOGFILE_MAXSIZE,
                                   LOGFILE_BACKUP_COUNT)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOGFILE_FORMAT))
logger.addHandler(file_handler)
#app.debug_log_format = '%(relativeCreated)-6d [%(process)-5d:%(thread)#x] %(levelname)-5s %(message)s [in %(module)s @ %(pathname)s:%(lineno)d]'
#app.logger.setLevel(logging.DEBUG)

if not os.path.exists(log_path):
    try:
        print ("=======hkjjjkhkhkjhkh££%£$^^")
        os.makedirs(os.path.dirname(log_path))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

# Log startup
logger.info('---------- Starting up!')
logger.info('__name__ is \'%s\'' % __name__)
logger.debug('Loading default config file from \'%s\'' % default_cfg_file)
logger.debug('Looking for custom app config in \'%s\'' % os.path.join(app.instance_path, 'app.cfg'))

