"""
Copyright (c) 2022 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import configparser
import argparse
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description='Running the application.'
)

parser.add_argument('-l', '--log', dest='log', type=str, default="",
                    help='The log write to file\npython main.py --log out.log')
parser.add_argument('-d', '--debug', dest='debug', action="store_true", default=False,
                    help='Debug mode\n-d or --debug')
parser.add_argument('-cc', '--cache', dest='cache', action="store_true", default=False,
                    help='Use requests cache\n-cc or --cache')

args = parser.parse_args()
config = configparser.ConfigParser()
config.read("config.ini")

import requests as _requests
import requests_cache
# Кешируем запросы
CACHE = args.cache
if CACHE:
    requests_cache.install_cache('requests_cache')
from tool import log, Handler
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Any, List
import os
from datetime import datetime


if args.log:
    logger = log(__name__, args.log)
else:
    logger = log(__name__)

BASE_URL = ""
DEBUG = args.debug
REPORT_PATH = os.path.join(os.getcwd(), datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".csv")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
}

@dataclass
class IData:
    name: str
    value: Any


class BaseParserException(Exception):
    """Базовое исключение"""
    pass


class NotUrlsException(BaseParserException):
    """Если нет каких то ссылок"""
    pass


class BadStatusCode(BaseParserException):
    """Сервер вернул плохой ответ"""
    pass


class ConnectionError(BaseParserException):
    """Проблемы с соединением"""
    pass


class Requests:
    """Класс обертка над библиотекой requests"""

    class Response:
        """Регистрация """
        def __init__(self, url, status_code):
            self.url = url
            self.status_code = status_code
            self.type_url = None

    _response_list: List[Response] = []
    COUNT = 0

    def get(self, *args, **kwargs):
        """get запрос"""
        Requests.COUNT += 1
        url = args[0]
        try:
            res = _requests.get(*args, **kwargs)
            Requests._response_list.append(self.Response(url, res.status_code))
            if res.status_code == 200:
                logger.info(f"Response [{res.status_code}] {url}")
            else:
                logger.warning(f"Status code: {res.status_code} {url}")
                raise BadStatusCode(f"Bad status code: {res.status_code}")
        except _requests.exceptions.ConnectionError:
            Requests._response_list.append(self.Response(url, 900))
            logger.warning(f"Connection Error {url}")
            raise ConnectionError(f"Problem with {url} ")

        return res

    def post(self, *args, **kwargs):
        """post запрос"""
        pass

    def __del__(self):
        logger.info(self.requests_report())

    def requests_report(self):
        """Вывод статистики по парсингу"""
        status200 = list(filter(lambda x: x.status_code == 200, self._response_list))
        statusBad = list(filter(lambda x: x.status_code != 200, self._response_list))
        string = f"\n{'-'*14} requests result {'-'*14}\n" \
                 f"Urls {Requests.COUNT}\n" \
                 f"Good {len(status200)}\n" \
                 f"Bad  {len(statusBad)}\n" \
                 f"{'-'*45}"
        return string


requests = Requests()


class Product:
    """Объект парсинга"""
    products = []
    COLUMN_NAME = []

    def __init__(self, url):
        pass

    def dump_csv(self):
        pass

    @staticmethod
    def get_soup(html: str) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        return soup


class FunctionUnit:
    """Функциональный блок"""
    SHARE_DATA:IData = None

    def __init__(self, func):
        self.func = func

    def run(self):
        self.func(FunctionUnit)

    def __call__(self, *args, **kwargs):
        self.func(FunctionUnit)


def search_content(cls: FunctionUnit):
    pass


def end_parsing(cls: FunctionUnit):
    pass


def main():
    unit01 = FunctionUnit(search_content)
    unit02 = FunctionUnit(end_parsing)
    unit01.run()
    unit02.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.debug("\n >>> Stop. CTRL+C")
    finally:
        del requests
