from bs4 import BeautifulSoup
import requests
import re
import pprint
from urllib.parse import urljoin
from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import *

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

def furure_weekday(str_month):
    """

    :param str_month: Переводит строку с будущеи днем недели в формат datetime, например 2019-02-24
    :return:
    """
    if 'понедел' in str_month:
        return date.today() + relativedelta(weekday=MO)
    elif 'вторник' in str_month:
        return date.today() + relativedelta(weekday=TU)
    elif 'сред' in str_month:
        return date.today() + relativedelta(weekday=WE)
    elif 'четверг' in str_month:
        return date.today() + relativedelta(weekday=TH)
    elif 'пятниц' in str_month:
        return date.today() + relativedelta(weekday=FR)
    elif 'суббот' in str_month:
        return date.today() + relativedelta(weekday=SA)
    elif 'воскресен' in str_month:
        return date.today() + relativedelta(weekday=SU)

def MonthRefactor(str_month):
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


def www32_top_ru(url_page):
    """

    Данные подгружаются по Ajax методом Post до 8 отзывов на странице.
    :param url_page: Страница клиники или врача
    :return:
    """
    if url_page.find("clinics") != -1:
        type = "clinic"
    elif(re.search(r"\bdr\b", url_page) != None):
        type = "doctor"
    else:
        raise Exception("Не был определен тип страницы")


    id_search = re.search(r"\b\d+\b", url_page)
    if id_search != None:
        id = id_search.group(0)
    else:
        raise Exception("Не определен Id по ссылке")

    main_url = "https://www.32top.ru/Controller/ajax/"
    url_site = "https://www.32top.ru/"
    query_string = {"JsHttpRequest": "0-xml"}

    #Cчетчики
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0

    comment_list = []
    #Текущая страница pagination
    current_page = 1

    while True:
        print("Текущая страница pagination:", current_page)
        if(type is "clinic"):
            payload = "call=Component_Comment_Roll/index&params[service]=0&params[modelName]=Clinic&params[modelId]=" +\
                      str(id) + "&params[rate]=all&params[commentId]=0&params[sort]=&params[page]=" + str(current_page)
        elif(type is "doctor"):
            payload = "call=Component_Comment_Roll/index&params[service]=0&params[modelName]=Doctor&params[modelId]="+ \
                      str(id) +"&params[rate]=all&params[commentId]=&params[sort]=&params[page]=" + str(current_page)

        respon = requests.request("POST", main_url, data=payload, params=query_string).json()
        html = get_html(respon["js"]["result"]["html"])

        if(type is "clinic"):
            items = html.select('#clinicComments > div[itemprop = "review"]')
        elif(type is "doctor"):
            items = html.select('#clinicComments> div[itemscope=""]')
        print("Количество:", len(items))

        #Если нету, то значит отзывы закончились
        if(len(items) == 0):
            break

        for item in items:
            author_name = item.select('span[itemprop = "author"] > div')[0].text.strip()

            date = item.find("span", "comment-grey").text.strip()
            if date.find("Сегодня") != -1:
                date = datetime.now().strftime("%YYYY-%m-%d")
            else:
                try:
                    #Регулярка, ищет цифры в начале строки
                    day = int(re.search("^\d+", date).group(0))

                    month = int(MonthRefactor(date))
                    #Регулярка, поиск чисел с длинной 3 или 4 цифры
                    text_search = re.search("\d{3,4}", date)
                    if (text_search is not None):
                        year = int(text_search.group(0))

                    else:
                        year = datetime.now().year

                    date = datetime(year, month, day).strftime("%Y-%m-%d")
                except AttributeError:
                    date = furure_weekday(date)

            emotion = item.find("span", {"itemprop" : "reviewRating"}).find("div").get("class")[0]

            if emotion == "positive":
                count_positive_comments += 1
            elif emotion == "negative":
                count_negative_comments += 1
            elif emotion == "neutral":
                count_neitral_comments += 1
            text = item.find("div", "comment-text").text.strip()

            url = urljoin(url_site, item.find("link").get("href"))
            #Количество комментариев следующего уровня
            subcomments = item.select('div[itemprop = "review"]')
            if(len(subcomments) > 0):
                response = "yes"
            else:
                response = "no"
            comment = {
                'author_name': author_name,
                'date': date,
                'emotion': emotion,
                'text': text,
                'response': response,
                'url': url
            }
            comment_list.append(comment)

        current_page += 1

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

def all_parsers():
    # www32_top_ru("https://www.32top.ru/dr/10545-stepanov-andrey-vasilevich/")
    www32_top_ru("https://www.32top.ru/clinics/588/")


if __name__ == '__main__':
    all_parsers()
