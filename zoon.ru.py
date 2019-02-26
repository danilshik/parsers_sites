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


def parser(url_main):
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    count_none_comments = 0
    comment_list = []

    r = requests.request("GET", url_main).content
    html = get_html(r)
    id = html.select_one("div.comments-section.service-feedbacks.service-box-white.js-togglable-content.js-reviews-module.js-corpservice-block").get("data-owner-id")
    print(id)

    url_page = "https://spb.zoon.ru/js.php?area=service&action=CommentList&owner[]=organization&owner[]=prof&organization=" + id
    json = requests.request("GET", url_page).json()
    # print(json)
    html = get_html(json["list"])

    items = html.select('body > li')
    print(len(items))
    for item in items:

        block_data_emotion = item.select_one('span.gray')

        date = block_data_emotion.text.split("\n")[-1].strip()
        date_block = date.split(" ")
        day = date_block[0]
        if(len(day) == 1):
            day = "0" + day
        month = MonthRefactor(date_block[1])
        if(date_block[2].isdigit()):
            year = date_block[2]
        else:
            year = str(datetime.now().year)

        date = year + "-" + month + "-" + day

        author_name = item.get("data-author")

        try:
            emotion_text = block_data_emotion.select('span.star-item > span[style="width: 100%; display: block;"]')
            if(len(emotion_text) == 0):
                emotion = None
                count_none_comments += 1
            elif (len(emotion_text) >= 4.5):
                emotion = "positive"
                count_positive_comments += 1

            elif((len(emotion_text) <= 2) and (len(emotion_text) != 0)):
                emotion = "negative"
                count_negative_comments += 1
            else:
                emotion = "neutral"
                count_neitral_comments += 1
        except Exception as e:
            emotion = None
            print(e)
        response_block = item.select_one("ul.list-reset.subcomments > li")
        if response_block is None:
            response = "no"
        else:
            response = "yes"

        text = item.select_one("div.js-comment-short-text").text.strip()
        text = text.replace("\xa0", " ")

        comment = {
            'author_name': author_name,
            'date': date,
            'emotion': emotion,
            'text': text,
            'response': response,
            'url': url_main
        }
        print(comment)
        comment_list.append(comment)

    statistic = {
        'count': count_positive_comments + count_negative_comments + count_neitral_comments + count_none_comments,
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
    parser("https://spb.zoon.ru/medical/mrt_tsentr_i_klinika_riorit_na_metro_grazhdanskij_prospekt/")
    # parser("https://spb.zoon.ru/p-doctor/nargiza_charyevna_dzhumaeva/")