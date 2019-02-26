from bs4 import BeautifulSoup
import requests
import re
import pprint
from urllib.parse import urljoin
from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import *
import json
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

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

def get_html (request):
    return BeautifulSoup(request, 'lxml')

def parser(id):
    """

    :param id: идентификатор клиники, парсинг происходит по разбору Ajax запросу
    :return:
    """
    url_page = "https://www.yell.ru/company/reviews/"
    page = 1
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    while True:
        params = {
            "id" : str(id),
            "page" : page,
            "sort" : "recent"
        }
        r = requests.request("GET", url_page, params=params).content
        print("Pagination", page)
        html = get_html(r)
        # print(html)
        items = html.select("div.reviews__item")
        if (len(items) == 0):
            break
        for item in items:
            try:
                date = item.select_one("span.reviews__item-added").text.strip()
                date_block = date.split(" ")
                day = date_block[0]
                month = MonthRefactor(date_block[1])
                year = date_block[2]
                date = year + "-" + month + "-" + day
            except:
                date = None

            author_name = item.select_one("div.reviews__item-user-name").text.strip()

            try:
                emotion_text = float(item.select_one("span.rating__value").text.strip())
                if (emotion_text >= 4.5):
                    emotion = "positive"
                    count_positive_comments += 1

                elif (emotion_text <= 2):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except Exception as e:
                emotion = None
                print(e)
            response_block = item.select_one("div.repliesreplies_theme_light.ng-scope > div")
            if response_block is None:
                response = "no"
            else:
                response = "yes"

            text = item.select_one("div.reviews__item-text").text.strip()
            url = item.select_one("div.share").get("data-url")

            comment = {
                'author_name': author_name,
                'date': date,
                'emotion': emotion,
                'text': text,
                'response': response,
                'url': url
            }
            print(comment)
            comment_list.append(comment)


        page += 1

    statistic = {
        'count': count_positive_comments + count_negative_comments + count_neitral_comments,
        'positive': count_positive_comments,
        'negative': count_negative_comments,
        'neutral': count_neitral_comments
    }
    main_dict = {
        'statistic': statistic,
        'comments': comment_list
    }

    pprint.pprint(main_dict)
    return main_dict



if __name__ == '__main__':
    parser(8980641)