"""
Copyright (c) 2021 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""

import requests as _requests
import requests_cache
# Кешируем запросы
CACHE = True
if CACHE:
    requests_cache.install_cache('requests_cache')
from tool import log
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Any, List


logger = log(__name__)
BASE_URL = ""


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

    _response_list: List[Response] = []
    COUNT = 0

    def get(self, *args, **kwargs):
        """get запрос"""
        Requests.COUNT += 1
        url = args[0]
        try:
            res = _requests.get(*args, **kwargs)
            if res.status_code == 200:
                Requests._response_list.append( self.Response(url, res.status_code) )
                logger.info(f"Response [{res.status_code}] {url}")
            else:
                logger.warning(f"Status code: {res.status_code} {url}")
                raise BadStatusCode(f"Bad status code: {res.status_code}")
        except _requests.exceptions.ConnectionError:
            logger.warning(f"Connection Error {url}")
            raise ConnectionError(f"Problem with {url} ")

        return res

    def post(self, *args, **kwargs):
        """post запрос"""
        pass

    def __del__(self):
        """Вывод статистики по парсингу"""
        status200 = list(filter(lambda x: x.status_code == 200, self._response_list))
        string = f"\n===== requests result =====\n" \
                 f"<urls: {Requests.COUNT}>\n" \
                 f"<status_200: {len(status200)}>\n"
        logger.info(string)


requests = Requests()


class Product:
    """Объект парсинга"""
    products = []
    COLUMN_NAME = []

    def __init__(self, url):
        pass

    def dump_csv(self):
        pass


class FunctionUnit:
    """Функциональный блок"""
    SHARE_DATA:IData = None

    def __init__(self, func):
        self.func = func

    def run(self):
        self.func(FunctionUnit)

    def __call__(self, *args, **kwargs):
        self.func(FunctionUnit)

    @staticmethod
    def get_soup(html: str) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        return soup


def search_content(cls: FunctionUnit):
    pass


def end_parsing(cls: FunctionUnit):
    global requests
    del requests


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
