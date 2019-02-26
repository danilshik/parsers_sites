from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import *
from bs4 import BeautifulSoup


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


def get_html(request):
    return BeautifulSoup(request, 'lxml')

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
