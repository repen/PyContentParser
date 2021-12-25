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
import os
import csv
from datetime import datetime


logger = log(__name__)
BASE_URL = "http://books.toscrape.com"
REPORT_PATH = os.path.join(os.getcwd(), datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".csv")
TEMPLATE01 = "page-{}.html"


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


class Book:
    """Объект парсинга"""
    urls = []
    COLUMN_NAME = [
        "NAME",
        "ID",
        "TYPE",
        "EXCL PRICE",
        "INCL PRICE",
        "TAX",
        "AVAILABILITY",
        "DESCRIPTION",
        "IMAGE"
    ]

    def __init__(self, url, category):
        self.url = url
        self.category = category
        response = requests.get(self.url)
        response.encoding = "utf8"
        soup = FunctionUnit.get_soup(response.text)
        meta_table = soup.select_one("table")
        meta_dict = {x.th.text.strip():x.td.text.strip() for x in meta_table.select("tr")}

        self.image = BASE_URL + soup.select_one("#product_gallery img")['src'].replace("../..", "")
        self.name = soup.h1.text.strip()
        self.description = soup.select_one("#product_description ~ p")
        self.upc = meta_dict['UPC']
        self.type = meta_dict["Product Type"]
        self.excl_price = meta_dict["Price (excl. tax)"]
        self.incl_price = meta_dict["Price (incl. tax)"]
        self.tax = meta_dict["Tax"]
        self.availability = meta_dict['Availability']
        self.number_reviews = meta_dict["Number of reviews"]

        self.attribute_row = [
            self.name, self.upc, self.type, self.excl_price, self.incl_price,
            self.tax, self.availability, self.description, self.image
        ]

        self.dump_csv()

    def dump_csv(self):
        with open(REPORT_PATH, mode='a', encoding="utf8") as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            if Book.COLUMN_NAME:
                writer.writerow(Book.COLUMN_NAME)
                Book.COLUMN_NAME.clear()
            writer.writerow(self.attribute_row)


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


def collect_category(cls: FunctionUnit):
    """собираем ссылки на категории"""
    response = requests.get("http://books.toscrape.com/index.html")
    soup = FunctionUnit.get_soup(response.text)
    category_list = []
    for category in soup.select(".side_categories ul li ul li"):
        url = BASE_URL + "/" + category.a['href']
        category_list.append(url)

    # подготавливаем данные для следующей функции
    cls.SHARE_DATA = IData("The category list", category_list)


def extract_links(html):
    soup = FunctionUnit.get_soup(html)
    category_name = soup.select_one("h1").text.strip()
    items = soup.select("section div ol li")
    for item in items:
        url = f"{BASE_URL}/catalogue/{item.select_one('a')['href'].replace('../../../', '')}"
        Book.urls.append((url, category_name))


def recursive_collect_url(url, index=1):
    """
    url example
    One page
    http://books.toscrape.com/catalogue/category/books/travel_2/index.html

    Multiple page
    http://books.toscrape.com/catalogue/category/books/mystery_3/page-1.html
    http://books.toscrape.com/catalogue/category/books/mystery_3/page-2.html
    """

    new_url = url.replace("index.html", TEMPLATE01)
    try:
        response = requests.get(new_url.format(index))
        extract_links(response.text)
        recursive_collect_url(url, index + 1)
    except BadStatusCode:
        try:
            response = requests.get(url)
            extract_links(response.text)
        except BadStatusCode:
            return


def collect_link(cls: FunctionUnit):
    """собираем ссылки на книги"""
    category_list = cls.SHARE_DATA.value
    for url in category_list:
        recursive_collect_url(url)


def extract_data(cls: FunctionUnit):
    """
    Извлекаем данные в 1 поток
    Можно реализовать многопоточный сбор.
    """
    for item in Book.urls:
        url = item[0]
        category_name = item[1]
        Book(url, category_name)


def end_parsing(cls: FunctionUnit):
    global requests
    del requests


def main():
    unit01 = FunctionUnit(collect_category)
    unit02 = FunctionUnit(collect_link)
    unit03 = FunctionUnit(extract_data)
    unit04 = FunctionUnit(end_parsing)

    unit01.run()
    unit02.run()
    unit03.run()
    unit04.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.debug("\n >>> Stop. CTRL+C")
