"""
Copyright (c) 2022 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""

import logging
import hashlib
import os
import time
import re
from functools import partial
from dataclasses import dataclass

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

    class Base:

        def __init__(self, section, config, main_dict: dict):
            self.section = section
            self.main_dict = main_dict
            self.functions = list()

            for key in config[section]:
                func = getattr(self, key)
                self.functions.append(partial(func, config[section][key]))

        def get_functions(self):
            return self.functions

    class Key(Base):

        def func01(self, template):
            key, slice = parsing_config(template)
            slice = int(slice)
            value = self.main_dict.pop(key)
            slice = int(slice)
            key = key[:-slice]
            self.main_dict[key] = value

        def all_replace(self, templates: str):
            # all_replace идет первая по приоретету
            for template in re.split(r"\s?\|\s?", templates):
                pattern, repl = parsing_config(template)
                new_dict = dict()
                for key, value in self.main_dict.items():
                    new_dict[re.sub(pattern, repl, key)] = value
                self.main_dict.clear()
                self.main_dict.update(new_dict)

    class Value(Base):

        def all_replace(self, templates: str):
            for template in re.split(r"\s?\|\s?", templates):
                pattern, repl = parsing_config(template)
                for key, value in self.main_dict.items():
                    self.main_dict[key] = re.sub(pattern, repl, value)

        def brand(self, templates: str):
            key, count = parsing_config(templates)
            count = int(count)
            self.main_dict[key] = self.main_dict[key] * count

    def __init__(self, config, main_dict: dict):
        self.handler_key = Handler.Key("key", config, main_dict)
        self.handler_value = Handler.Value("value", config, main_dict)
        self.key_map()
        self.value_map()

    def key_map(self):
        for func in self.handler_key.get_functions():
            func()

    def value_map(self):
        for func in self.handler_value.get_functions():
            func()

