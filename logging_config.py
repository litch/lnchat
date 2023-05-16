import logging, datetime, sys, json, traceback
from logging.handlers import TimedRotatingFileHandler
import os 

FUNDS_TRANSFERRING = "FUNDS_TRANSFERRING"

class ErrorFilter(object):
    def __init__(self):
        self.__level = logging.ERROR

    def filter(self, logRecord):
        return logRecord.levelno == self.__level

def log_uncaught_exceptions(ex_type, value, tb):
    logger = logging.getLogger("")
    logger.error(
        f"Uncaught exception: type {str(ex_type)}, value {str(value)}")
    logger.error(''.join(traceback.format_exception(ex_type, value, tb)))
    sys.__excepthook__(ex_type, value, tb)


def configure(config):
    logger = logging.getLogger('')
    log_root = config["logging"]["log_dir"]
    os.makedirs(log_root, exist_ok=True)
    config_root_logger()
    config_root_file_logger(logger, log_root)
    config_error_logger(logger, log_root)
    config_funds_transferring_logging(log_root)

def config_root_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sys.excepthook = log_uncaught_exceptions


def config_root_file_logger(logger, log_root):
    fh = TimedRotatingFileHandler(
        log_root + '/amboss-fulfillment.log',
        utc=True,
        when="D",
        atTime=datetime.time(11, 00))
    fh.suffix = "%Y%m%d"
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def config_error_logger(logger, log_root):
    eh = TimedRotatingFileHandler(
        log_root + '/error.log',
        utc=True,
        when="D",
        atTime=datetime.time(11, 00))
    eh.suffix = "%Y%m%d"
    eh.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    eh.setFormatter(formatter)
    eh.addFilter(ErrorFilter())
    logger.addHandler(eh)


def config_funds_transferring_logging(log_root):
    funds_logger = logging.getLogger(FUNDS_TRANSFERRING)
    fh = TimedRotatingFileHandler(
        log_root + '/funds_movements.json',
        utc=True,
        when="D",
        atTime=datetime.time(11, 00))
    fh.suffix = "%Y%m%d"
    fh.setLevel(logging.DEBUG)
    funds_logger.addHandler(fh)
    return funds_logger

def config_query_logger(log_root):
    query_logger = logging.getLogger("query_logger")
    fh = TimedRotatingFileHandler(
        log_root + '/query.log',
        utc=True,
        when="D",
        atTime=datetime.time(11, 00))
    fh.suffix = "%Y%m%d"
    fh.setLevel(logging.DEBUG)
    query_logger.addHandler(fh)
    return query_logger