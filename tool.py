"""
Copyright (c) 2022 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import traceback
import logging
import hashlib
import os
import time
import re
from functools import partial
from typing import Dict, List


def hash_(string):
    return hashlib.sha1(string.encode()).hexdigest()


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def timeit(f):

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        # log.info( "Time run {} {}".format(te-ts, str(f)) )
        print( "Time run {} {}".format(te-ts, str(f)) )
        return result

    return timed


def log(name, filename=None):
    # создаём logger
    logger = logging.getLogger(name)
    logger.setLevel( logging.DEBUG )

    # создаём консольный handler и задаём уровень
    if filename:
        ch = logging.FileHandler(os.path.join(  os.getcwd(), filename ))
    else:
        ch = logging.StreamHandler()

    ch.setLevel(logging.DEBUG)

    # создаём formatter
    formatter = logging.Formatter('%(asctime)s : %(lineno)d : %(name)s : %(levelname)s : %(message)s')
    # %(lineno)d :
    # добавляем formatter в ch
    ch.setFormatter(formatter)

    # добавляем ch к logger
    logger.addHandler(ch)

    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')
    return logger


def parsing_config(string) -> tuple:
    return tuple([re.sub(r"^\/|/$", "", x) for x in re.split(r"(?<!^)(?<!\\)/(?!$)", string)])


class Handler:
    """Обработка данных."""
    class product:
        def __init__(self, data_list: List[Dict]):
            self.data_list = data_list
