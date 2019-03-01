from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import *
from bs4 import BeautifulSoup
from requests.auth import HTTPProxyAuth
index_proxy = 0
proxy_list = [
    "http;207.164.21.34:3128;u5aX8c;LCTkNM",
    "http;185.233.81.118:9401;u5aX8c;LCTkNM",
    "http;185.233.80.187:9937;u5aX8c;LCTkNM"
]

def get_proxy():
    global index_proxy
    proxy = proxy_list[index_proxy]
    index_proxy += 1
    if(index_proxy == len(proxy_list)):
        index_proxy = 0

    proxy_block = proxy.split(";")
    proxies = {proxy_block[0]: proxy_block[1]}
    auth = HTTPProxyAuth(proxy_block[2], proxy_block[3])
    return [proxies, auth]

def last_year(last_year):
    """

    :param last_year: это сколько лет назад, например сейчас 2019, чтобы получить 2017, нужно передать 2
    :return:
    """
    return date.today() - relativedelta(years=last_year)

def last_weekday(str_month):
    """

    :param str_month: Переводит строку с прошлым днем недели в формат datetime, например 2019-02-24
    :return:
    """
    if 'понедел' in str_month:
        return date.today() - relativedelta(weekday=MO(-1))
    elif 'вторник' in str_month:
        return date.today() + relativedelta(weekday=TU(-1))
    elif 'сред' in str_month:
        return date.today() + relativedelta(weekday=WE(-1))
    elif 'четверг' in str_month:
        return date.today() + relativedelta(weekday=TH(-1))
    elif 'пятниц' in str_month:
        return date.today() + relativedelta(weekday=FR(-1))
    elif 'суббот' in str_month:
        return date.today() + relativedelta(weekday=SA(-1))
    elif 'воскресен' in str_month:
        return date.today() + relativedelta(weekday=SU(-1))


def get_html(request, type):
    return BeautifulSoup(request, type)

def MonthRefactor(str):
    str_month = str.lower()
    if 'январ' in str_month:
        return('01')
    elif 'феврал' in str_month:
        return('02')
    elif 'март' in str_month:
        return('03')
    elif 'апрел' in str_month:
        return('04')
    elif 'май' in str_month or 'мая' in str_month:
        return('05')
    elif 'июн' in str_month:
        return('06')
    elif 'июл' in str_month:
        return('07')
    elif 'август' in str_month:
        return('08')
    elif 'сентябр' in str_month:
        return('09')
    elif 'октябр' in str_month:
        return('10')
    elif 'ноябр' in str_month:
        return('11')
    elif 'декабр' in str_month:
        return('12')


