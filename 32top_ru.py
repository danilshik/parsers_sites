import requests
import re
import pprint
from datetime import *
from urllib.parse import urljoin
import parse_helper as ph

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

def parser(id, type, url_page):
    """

    Данные подгружаются по Ajax методом Post до 8 отзывов на странице.
    :param url_page: Страница клиники или врача
    :param id: Идентификатор больницы или доктора, можно получить в элементе, который ищется в 37 строчке
    :param type: тип clinic или doctor
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
            html = ph.get_html(r)

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
    count = 0

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
        proxy = ph.get_proxy()
        respon = requests.request("POST", main_url, data=payload, params=query_string, proxies=proxy[0], auth=proxy[1]).json()
        html = ph.get_html(respon["js"]["result"]["html"])

        if(type is "clinic"):
            items = html.select('#clinicComments > div[itemprop = "review"]')
        elif(type is "doctor"):
            items = html.select('#clinicComments> div[itemscope=""]')
        print("Количество:", len(items))

        #Если нету, то значит отзывы закончились
        if(len(items) == 0):
            break

        for item in items:
            count += 1
            author_name = item.select('span[itemprop = "author"] > div')[0].text.strip()

            date = item.find("span", "comment-grey").text.strip()
            if date.find("Сегодня") != -1:
                date = datetime.now().strftime("%YYYY-%m-%d")
            else:
                try:
                    #Регулярка, ищет цифры в начале строки
                    day = int(re.search("^\d+", date).group(0))

                    month = int(ph.MonthRefactor(date))
                    #Регулярка, поиск чисел с длинной 3 или 4 цифры
                    text_search = re.search("\d{3,4}", date)
                    if (text_search is not None):
                        year = int(text_search.group(0))

                    else:
                        year = datetime.now().year

                    date = datetime(year, month, day).strftime("%Y-%m-%d")
                except AttributeError:
                    date = str(ph.last_weekday(date))

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
        'count': count,
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
    parser(10545, "doctor", "https://www.32top.ru/dr/10545-stepanov-andrey-vasilevich/")
    # www32_top_ru(10545, "doctor", None)
    # www32_top_ru(None, None, "https://www.32top.ru/dr/10545-stepanov-andrey-vasilevich/")
