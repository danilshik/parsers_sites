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


def www32_top_ru(id, type, url_page):
    """

    Данные подгружаются по Ajax методом Post до 8 отзывов на странице.
    :param url_page: Страница клиники или врача
    :return:
    """
    if ((type != "clinic") and (type != "doctor") and (type is not None)):
        raise Exception("Неправильно указан входный тип. Возможно: clinic, doctor или None")


    if type is None:

        if url_page.find("clinics") != -1:
            type = "clinic"
        elif(re.search(r"\bdr\b", url_page) != None):
            type = "doctor"
        else:
            raise Exception("Не был определен тип страницы")

        if id is None:
            r = requests.request("GET", url_page).content
            html = get_html(r)

            if type is "clinic":
                id = html.select_one("input.js-clinic_id.hidden").get("value")

            elif type is "doctor":
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
                    date = str(last_weekday(date))

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

def www_kleos_ru(id, type):
    """

    :param id: id специалиста или организации
    :param type: или doctor или clinic
    :return:
    """

    is_last = False
    # Cчетчики
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    comment_id_list = []

    if id is None:
        raise Exception("Не указан id")


    if type is "clinic":
        item_name = "org"
    elif type is "doctor":
        item_name = "specialist"
    else:
        raise Exception("Указан неправильный type")

    while is_last != True:
        params = {'last_ids[]': comment_id_list}
        r = requests.request("GET", "https://www.kleos.ru/comment/0/operation?mode=getlist&item_id=" + str(id) + "&item_name=" + item_name + "&comment_cnt=1000000",
                             headers=headers, params=params).content
        html = get_html(r)
        json_text = json.loads(html.select_one("p").text)
        html_json = get_html(json_text["html"])
        if(json_text["is_last"] == True):
            is_last = True
        items = html_json.select("body > div.comment-item")
        print("Количество отзывов:", len(items))
        # items= items[:1]
        for item in items:
            subcomments = item.select("div.comment-item")
            if(len(subcomments) > 0):
                response = "yes"
            else:
                response = "no"
            comment_id = item.get("data-id")
            comment_id_list.append(comment_id)
            left_block = item.select_one("div.left-content > div")
            spans = left_block.select("span")

            date = spans[0].text.strip().replace(".", "-")

            author_name = spans[1].text.strip()

            try:
                emotion_text = float(left_block.select_one("div.star-rating-svg").get("data-initial-rating"))
                if(emotion_text >= 4.5):
                    emotion = "positive"
                    count_positive_comments += 1

                elif(emotion_text <= 2):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except:
                emotion = None

            text = item.select_one("div.comment-text.padding-coment").text.strip()
            url = None

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

def startsmile_ru(url_page):
    """
    Парсинг производится по HTML.
    :param url_page: ссылка на страницу или клинику
    :return:
    """
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0

    comment_list = []

    r = requests.request("GET", url_page).content
    html = get_html(r)
    # print(html)
    items = html.select("ul.doc-main__feedbacks__list > li")
    for item in items:
        date = item.select_one("div.doc-main__feedbacks__item-date").text.strip()
        date_block = date.split(" ")
        day = date_block[0]
        month = MonthRefactor(date_block[1])
        year = date_block[2]
        date = year + "-" + month + "-" + day

        author_name = item.select_one("a.permalink").text.strip()

        try:
            emotion_text = float(item.select_one("div.best__c-b-r-count.value").text.strip())
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
        try:
            subcomments = html.select_one("div.comment-box")
            response = "yes"
        except:
            response = "no"

        text = item.select_one("div.doc-main__feedbacks__item-text.description").text.strip()
        url = url_page

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

def yell_ru(id):
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

def zoon_ru(url_main):
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
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
    # www32_top_ru(10545, "doctor", "https://www.32top.ru/dr/10545-stepanov-andrey-vasilevich/")
    # www32_top_ru(10545, "doctor", None)
    # www32_top_ru(None, None, "https://www.32top.ru/dr/10545-stepanov-andrey-vasilevich/")

    # www_kleos_ru(7493, "clinic")
    # www_kleos_ru(1696, "doctor")
    # startsmile_ru("https://www.startsmile.ru/stomatologi/akhtanin_aleksandr_pavlovich.html")
    # yell_ru(8980641)
    zoon_ru("https://spb.zoon.ru/medical/mrt_tsentr_i_klinika_riorit_na_metro_grazhdanskij_prospekt/")
    zoon_ru("https://spb.zoon.ru/p-doctor/nargiza_charyevna_dzhumaeva/")


if __name__ == '__main__':
    all_parsers()